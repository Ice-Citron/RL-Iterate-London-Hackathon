"""
ART-based GRPO Training for Security Agents

This module implements the full GRPO training loop using OpenPipe's ART library.
It integrates CAI-style rollouts with Claude MCP Judge for reward signals.

Usage:
    python -m src.training.art_trainer --config h100
"""

import asyncio
import argparse
import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

# Load secrets first
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from secretsConfig import ANTHROPIC_API_KEY, WANDB_API_KEY, HF_TOKEN
    os.environ.setdefault("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    os.environ.setdefault("WANDB_API_KEY", WANDB_API_KEY)
    os.environ.setdefault("HF_TOKEN", HF_TOKEN)
except ImportError:
    pass

# ART imports
try:
    import art
    from art.local import LocalBackend
    from art.utils import iterate_dataset, limit_concurrency
    HAS_ART = True
except ImportError:
    try:
        from openpipe import art
        from openpipe.art.local import LocalBackend
        from openpipe.art.utils import iterate_dataset, limit_concurrency
        HAS_ART = True
    except ImportError:
        HAS_ART = False
        print("Warning: ART not available. Install with: pip install openpipe-art[backend]")

# W&B imports
try:
    import wandb
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False

# HuggingFace imports
try:
    from huggingface_hub import HfApi
    HAS_HF = True
except ImportError:
    HAS_HF = False

from .config import TrainingConfig, H100_CONFIG, DEV_CONFIG, TINY_TEST_CONFIG
from .cai_integration import CAISecurityTools, FullCAIRollout, SecurityRolloutResult
from .challenges import get_challenges, get_training_curriculum, ALL_CHALLENGES


class JudgeClient:
    """Client for the Claude MCP Judge server"""

    def __init__(self, base_url: str = "http://localhost:8088"):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=120.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        try:
            client = await self.get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Judge health check failed: {e}")
            return False

    async def evaluate(
        self,
        task_description: str,
        agent_response: str,
    ) -> Dict[str, Any]:
        """Evaluate a trajectory with the Claude MCP judge"""
        client = await self.get_client()

        try:
            response = await client.post(
                "/verify",
                json={
                    "task_description": task_description,
                    "agent_response": agent_response,
                }
            )
            response.raise_for_status()
            result = response.json()

            return {
                "score": result.get("score", 0.0),
                "summary": result.get("summary", ""),
                "hallucination_detected": result.get("hallucination_detected", False),
                "verification_summary": result.get("verification_summary", ""),
            }
        except Exception as e:
            print(f"Judge evaluation failed: {e}")
            return {
                "score": 0.0,
                "summary": f"Evaluation error: {str(e)}",
                "hallucination_detected": False,
            }

    async def batch_evaluate(
        self,
        evaluations: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Batch evaluate multiple trajectories"""
        client = await self.get_client()

        try:
            response = await client.post(
                "/verify/batch",
                json={"evaluations": evaluations}
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"Batch evaluation failed: {e}")
            # Fall back to individual evaluations
            results = []
            for eval_req in evaluations:
                result = await self.evaluate(
                    eval_req["task_description"],
                    eval_req["agent_response"]
                )
                results.append(result)
            return results


def calculate_reward(
    judge_result: Dict[str, Any],
    rollout_result: SecurityRolloutResult,
    config: TrainingConfig,
) -> float:
    """
    Calculate final reward with all factors.

    Components:
    1. Base score from judge (-1.0 to 1.0)
    2. Hallucination penalty (force negative)
    3. Honest "I don't know" bonus
    4. Efficiency penalty for excessive tool calls
    """
    score = judge_result.get("score", 0.0)

    # 1. Hallucination penalty - force negative
    if judge_result.get("hallucination_detected"):
        return max(-1.0, min(-0.5, score - 0.5))

    # 2. Honest uncertainty bonus
    honest_phrases = [
        "i don't know",
        "i cannot determine",
        "insufficient information",
        "unable to complete",
        "i was unable to",
        "could not",
    ]
    final_output = rollout_result.final_output.lower()
    if any(phrase in final_output for phrase in honest_phrases):
        # Only bonus if they actually tried
        if rollout_result.total_tool_calls > 0:
            score += 0.3

    # 3. Efficiency penalty for excessive tool calls
    tool_calls = rollout_result.total_tool_calls
    if tool_calls > 30:
        penalty = min(0.3, (tool_calls - 30) * 0.01)
        score -= penalty

    # 4. Bonus for completing task successfully
    if rollout_result.success and score > 0:
        score = min(1.0, score + 0.2)

    return max(-1.0, min(1.0, score))


class SecurityPolicyConfig:
    """Policy configuration for security agent training"""

    def __init__(
        self,
        dvwa_url: str = "http://31.97.117.123",
        judge_url: str = "http://localhost:8088",
        max_tool_calls: int = 50,
        trajectories_per_group: int = 10,
        groups_per_step: int = 4,
        learning_rate: float = 1e-6,
        training_dataset_size: int = 16,
        val_set_size: int = 4,
        eval_steps: int = 5,
        num_epochs: int = 10,
    ):
        self.dvwa_url = dvwa_url
        self.judge_url = judge_url
        self.max_tool_calls = max_tool_calls
        self.trajectories_per_group = trajectories_per_group
        self.groups_per_step = groups_per_step
        self.learning_rate = learning_rate
        self.training_dataset_size = training_dataset_size
        self.val_set_size = val_set_size
        self.eval_steps = eval_steps
        self.num_epochs = num_epochs


if HAS_ART:
    @limit_concurrency(64)
    async def rollout_security_task(
        model: art.Model,
        challenge: Dict[str, Any],
        step: int = 0,
        phase: str = "train",
        config: SecurityPolicyConfig = None,
    ) -> art.Trajectory:
        """
        Execute a security challenge rollout and return an ART Trajectory.
        """
        config = config or SecurityPolicyConfig()

        # Create rollout handler with model's inference endpoint
        rollout = FullCAIRollout(
            model_base_url=model.inference_base_url,
            model_name=model.get_inference_name(),
            dvwa_url=config.dvwa_url,
            max_tool_calls=config.max_tool_calls,
        )

        # Execute the challenge
        result = await rollout.execute(challenge)

        # Get tool definitions for the trajectory
        tools = rollout.tools.get_openai_tools()

        # Create trajectory
        traj = art.Trajectory(
            messages_and_choices=result.messages,
            tools=tools,
            reward=0.0,  # Will be set after judge evaluation
            metadata={
                "challenge_id": challenge.get("id", "unknown"),
                "category": challenge.get("category", "general"),
                "difficulty": challenge.get("difficulty", "medium"),
                "training_step": str(step),
                "phase": phase,
                "model": model.name,
                "tool_calls": result.total_tool_calls,
                "claimed_success": result.success,
            },
        )

        # Evaluate with judge
        judge = JudgeClient(config.judge_url)
        try:
            judge_result = await judge.evaluate(
                task_description=challenge["task_description"],
                agent_response=result.final_output,
            )

            # Calculate final reward
            reward = calculate_reward(judge_result, result, None)
            traj.reward = reward
            traj.metadata["judge_score"] = judge_result.get("score", 0.0)
            traj.metadata["hallucination"] = judge_result.get("hallucination_detected", False)
            traj.metadata["judge_summary"] = judge_result.get("summary", "")[:200]

        except Exception as e:
            print(f"Judge evaluation failed for {challenge['id']}: {e}")
            traj.reward = -0.5  # Penalize failed evaluations
            traj.metadata["error"] = str(e)

        finally:
            await judge.close()

        # Add metrics
        traj.metrics = {
            "tool_calls": result.total_tool_calls,
            "claimed_success": 1 if result.success else 0,
            "hallucination": 1 if traj.metadata.get("hallucination") else 0,
        }

        traj.finish()
        return traj


    async def evaluate_model(
        model: art.Model,
        challenges: List[Dict[str, Any]],
        step: int,
        config: SecurityPolicyConfig,
    ) -> float:
        """Evaluate the model on validation challenges"""
        print(f"  Evaluating on {len(challenges)} challenges...")

        trajectories = await art.gather_trajectories(
            (
                rollout_security_task(model, challenge, step, "val", config)
                for challenge in challenges
            )
        )

        # Log to model
        await model.log(trajectories=trajectories, split="val")

        # Compute metrics
        total_reward = sum(t.reward for t in trajectories)
        avg_reward = total_reward / len(trajectories) if trajectories else 0

        successes = sum(1 for t in trajectories if t.reward > 0.5)
        hallucinations = sum(1 for t in trajectories if t.metadata.get("hallucination"))

        print(f"  Validation: avg_reward={avg_reward:.3f}, "
              f"success_rate={successes/len(trajectories):.2%}, "
              f"hallucination_rate={hallucinations/len(trajectories):.2%}")

        # Log to W&B
        if HAS_WANDB and wandb.run:
            wandb.log({
                "val/avg_reward": avg_reward,
                "val/success_rate": successes / len(trajectories),
                "val/hallucination_rate": hallucinations / len(trajectories),
            }, step=step)

        return avg_reward


    async def train_security_agent(
        model: art.TrainableModel,
        config: SecurityPolicyConfig,
        training_config: TrainingConfig,
    ):
        """
        Main training loop for security agent using GRPO.
        """
        print("\n" + "=" * 70)
        print("SECURITY AGENT GRPO TRAINING")
        print("=" * 70)
        print(f"Model: {model.name}")
        print(f"Base Model: {model.base_model}")
        print(f"DVWA URL: {config.dvwa_url}")
        print(f"Judge URL: {config.judge_url}")
        print("=" * 70 + "\n")

        # Initialize W&B
        if HAS_WANDB:
            wandb.init(
                project=training_config.wandb_project,
                entity=training_config.wandb_entity,
                config={
                    "model": model.name,
                    "base_model": model.base_model,
                    "learning_rate": config.learning_rate,
                    "trajectories_per_group": config.trajectories_per_group,
                    "groups_per_step": config.groups_per_step,
                },
                tags=["security-agent", "grpo", "rlaif", "dvwa"],
                name=f"{model.name}-{datetime.now().strftime('%Y%m%d-%H%M')}",
            )
            print(f"W&B initialized: {wandb.run.url}")

        # Load challenges
        all_challenges = get_training_curriculum()
        print(f"Loaded {len(all_challenges)} challenges")

        # Split into train/val
        random.shuffle(all_challenges)
        train_size = min(len(all_challenges) - config.val_set_size, config.training_dataset_size)
        train_challenges = all_challenges[:train_size]
        val_challenges = all_challenges[train_size:train_size + config.val_set_size]

        print(f"Training on {len(train_challenges)} challenges")
        print(f"Validation on {len(val_challenges)} challenges")

        with LocalBackend() as backend:
            # Register model with backend
            await model.register(backend)
            print(f"Model registered with inference at: {model.inference_base_url}")

            # Training loop
            train_iterator = iterate_dataset(
                list(range(len(train_challenges))),
                groups_per_step=config.groups_per_step,
                num_epochs=config.num_epochs,
                initial_step=await model.get_step(),
            )

            for batch in train_iterator:
                print(f"\n{'='*60}")
                print(f"STEP {batch.step} (Epoch {batch.epoch}, Step {batch.epoch_step})")
                print(f"{'='*60}")

                # Evaluation
                if batch.step % config.eval_steps == 0:
                    print("\n--- Evaluation ---")
                    await evaluate_model(model, val_challenges, batch.step, config)

                # Generate trajectory groups
                print(f"\nGenerating trajectories for {len(batch.items)} challenge groups...")
                batch_challenges = [train_challenges[i % len(train_challenges)] for i in batch.items]

                groups = await art.gather_trajectory_groups(
                    (
                        art.TrajectoryGroup(
                            (
                                rollout_security_task(
                                    model,
                                    challenge,
                                    batch.step,
                                    "train",
                                    config,
                                )
                                for _ in range(config.trajectories_per_group)
                            )
                        )
                        for challenge in batch_challenges
                    )
                )

                # Compute step metrics
                total_reward = sum(
                    sum(traj.reward for traj in group.trajectories)
                    for group in groups
                )
                num_trajectories = sum(len(group.trajectories) for group in groups)
                avg_reward = total_reward / num_trajectories if num_trajectories > 0 else 0

                hallucinations = sum(
                    sum(1 for t in g.trajectories if t.metadata.get("hallucination"))
                    for g in groups
                )
                successes = sum(
                    sum(1 for t in g.trajectories if t.reward > 0.5)
                    for g in groups
                )

                print(f"\nStep {batch.step} metrics:")
                print(f"  Trajectories: {num_trajectories}")
                print(f"  Avg reward: {avg_reward:.3f}")
                print(f"  Success rate: {successes/num_trajectories:.2%}")
                print(f"  Hallucination rate: {hallucinations/num_trajectories:.2%}")

                # Log to W&B
                if HAS_WANDB and wandb.run:
                    wandb.log({
                        "train/avg_reward": avg_reward,
                        "train/success_rate": successes / num_trajectories,
                        "train/hallucination_rate": hallucinations / num_trajectories,
                        "train/num_trajectories": num_trajectories,
                        "train/avg_tool_calls": sum(
                            sum(t.metrics.get("tool_calls", 0) for t in g.trajectories)
                            for g in groups
                        ) / num_trajectories,
                    }, step=batch.step)

                # GRPO training step
                print(f"\nTraining on {len(groups)} trajectory groups...")
                await model.train(
                    groups,
                    config=art.TrainConfig(learning_rate=config.learning_rate),
                )

                # Checkpoint
                if (batch.step + 1) % training_config.checkpoint_every == 0:
                    print(f"\nSaving checkpoint at step {batch.step + 1}...")
                    if HAS_HF and training_config.hf_repo_id and training_config.hf_token:
                        try:
                            # In production, would save LoRA weights here
                            print(f"  Would push to: {training_config.hf_repo_id}")
                        except Exception as e:
                            print(f"  Checkpoint push failed: {e}")

            # Final evaluation
            print("\n" + "=" * 60)
            print("FINAL EVALUATION")
            print("=" * 60)
            final_step = await model.get_step()
            final_reward = await evaluate_model(model, val_challenges, final_step, config)
            print(f"Final average reward: {final_reward:.3f}")

        # Cleanup
        if HAS_WANDB and wandb.run:
            wandb.finish()

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)


async def main_with_art():
    """Main entry point when ART is available"""
    parser = argparse.ArgumentParser(description="Security Agent GRPO Training")
    parser.add_argument(
        "--config",
        type=str,
        default="dev",
        choices=["dev", "h100", "tiny"],
        help="Configuration profile"
    )
    parser.add_argument("--judge-url", type=str, default="http://localhost:8088")
    parser.add_argument("--dvwa-url", type=str, default="http://31.97.117.123")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate")

    args = parser.parse_args()

    # Load config
    configs = {"dev": DEV_CONFIG, "h100": H100_CONFIG, "tiny": TINY_TEST_CONFIG}
    training_config = configs[args.config]

    # Create policy config
    policy_config = SecurityPolicyConfig(
        dvwa_url=args.dvwa_url,
        judge_url=args.judge_url,
        max_tool_calls=training_config.max_tool_calls,
        trajectories_per_group=training_config.rollouts_per_group,
        groups_per_step=training_config.groups_per_step,
        learning_rate=args.lr or training_config.learning_rate,
    )

    # Create trainable model
    model = art.TrainableModel(
        name=training_config.model_name,
        project=training_config.wandb_project,
        base_model=training_config.base_model,
    )

    # Configure internal settings for H100
    if args.config == "h100":
        model._internal_config = art.dev.InternalModelConfig(
            engine_args=art.dev.EngineArgs(
                tensor_parallel_size=training_config.tensor_parallel_size,
                enable_sleep_mode=True,
            ),
            init_args=art.dev.InitArgs(
                gpu_memory_utilization=training_config.gpu_memory_utilization,
                max_seq_length=training_config.max_seq_length,
                load_in_4bit=training_config.load_in_4bit,
            ),
            peft_args=art.dev.PeftArgs(
                r=training_config.lora_rank,
                lora_alpha=training_config.lora_alpha,
                lora_dropout=training_config.lora_dropout,
            ),
        )

    # Run training
    await train_security_agent(model, policy_config, training_config)


async def main_without_art():
    """Fallback main when ART is not available"""
    print("=" * 60)
    print("ART NOT AVAILABLE - MOCK TRAINING MODE")
    print("=" * 60)
    print("\nTo run actual training, install ART:")
    print("  pip install openpipe-art[backend]")
    print("\nRunning mock training to test integration...")

    # Test judge connectivity
    judge = JudgeClient("http://localhost:8088")
    if await judge.health_check():
        print("\nJudge server: OK")
    else:
        print("\nJudge server: NOT AVAILABLE")
        print("Start it with: uvicorn server:app --host 127.0.0.1 --port 8088")
        return

    # Test a mock rollout
    from .cai_integration import FullCAIRollout

    challenge = {
        "id": "test_challenge",
        "category": "sql_injection",
        "difficulty": "easy",
        "task_description": "Test SQL injection on DVWA /vulnerabilities/sqli/?id=",
    }

    print("\nTesting rollout (this will fail without a model server)...")
    # Can't test without model, but structure is in place

    await judge.close()
    print("\nMock training complete. Install ART for real training.")


def main():
    """Entry point"""
    if HAS_ART:
        asyncio.run(main_with_art())
    else:
        asyncio.run(main_without_art())


if __name__ == "__main__":
    main()

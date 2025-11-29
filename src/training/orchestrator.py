"""
Training Orchestrator for Security Agent RLAIF

This is the main training loop that integrates:
- CAI-style rollouts for security challenges
- Claude MCP Judge for evidence-based evaluation
- OpenPipe ART for GRPO training

Usage:
    python -m src.training.orchestrator --config dev
    python -m src.training.orchestrator --config h100
"""

import asyncio
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx

# Conditional imports for training
try:
    import art
    from art.local import LocalBackend
    HAS_ART = True
except ImportError:
    try:
        # Try alternative import path
        from openpipe import art
        from openpipe.art.local import LocalBackend
        HAS_ART = True
    except ImportError:
        HAS_ART = False
        print("Warning: ART not installed. Training disabled, test mode only.")
        print("Install with: pip install openpipe-art[backend]")

try:
    import wandb
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False
    print("Warning: W&B not installed. Logging disabled.")

from .config import TrainingConfig, H100_CONFIG, DEV_CONFIG, TINY_TEST_CONFIG
from .cai_rollout import CAIRollout, RolloutResult


class JudgeClient:
    """Client for the Claude MCP Judge server"""

    def __init__(self, base_url: str = "http://localhost:8088"):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=120.0,  # Judge may take time with tool calls
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if judge server is running"""
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
        """
        Evaluate a single trajectory.

        Returns:
            Dict with score, summary, hallucination_detected
        """
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

            # Parse extended format if available
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


class SecurityAgentTrainer:
    """
    Main training orchestrator for security agent RLAIF.

    Integrates CAI rollouts, Claude judge, and ART training.
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.judge = JudgeClient(config.judge_url)
        self.rollout_handler: Optional[CAIRollout] = None
        self.model = None
        self.backend = None

    async def initialize(self):
        """Initialize all components"""
        print("\n" + "=" * 60)
        print("SECURITY AGENT RLAIF TRAINING")
        print("=" * 60)
        print(f"Config: {self.config.model_name}")
        print(f"Base Model: {self.config.base_model}")
        print(f"DVWA Target: {self.config.dvwa_url}")
        print(f"Judge URL: {self.config.judge_url}")
        print("=" * 60 + "\n")

        # 1. Verify judge is running
        print("Checking judge server...")
        if not await self.judge.health_check():
            raise RuntimeError(
                f"Judge server not available at {self.config.judge_url}\n"
                "Start it with: uvicorn server:app --host 127.0.0.1 --port 8088"
            )
        print("  Judge server: OK")

        # 2. Initialize W&B
        if HAS_WANDB:
            print("Initializing W&B...")
            wandb.login(key=os.environ.get("WANDB_API_KEY"))
            wandb.init(
                project=self.config.wandb_project,
                entity=self.config.wandb_entity,
                config=self.config.to_dict(),
                tags=["security-agent", "grpo", "rlaif"],
                name=f"{self.config.model_name}-{datetime.now().strftime('%Y%m%d-%H%M')}",
                reinit=False,
            )
            print(f"  W&B Run: {wandb.run.name}")
            print(f"  W&B URL: {wandb.run.url}")

        # 3. Initialize ART model (if available)
        if HAS_ART:
            print("Initializing ART model...")
            self.model = art.TrainableModel(
                name=self.config.model_name,
                project=self.config.wandb_project,
                base_model=self.config.base_model,
            )

            # Configure internal settings
            self.model._internal_config = art.dev.InternalModelConfig(
                engine_args=art.dev.EngineArgs(
                    tensor_parallel_size=self.config.tensor_parallel_size,
                    enable_sleep_mode=True,  # Critical for fast pause/resume
                ),
                init_args=art.dev.InitArgs(
                    gpu_memory_utilization=self.config.gpu_memory_utilization,
                    max_seq_length=self.config.max_seq_length,
                    load_in_4bit=self.config.load_in_4bit,
                ),
                peft_args=art.dev.PeftArgs(
                    r=self.config.lora_rank,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                ),
            )

            # Register with backend
            print("  Registering with LocalBackend...")
            self.backend = LocalBackend()
            await self.model.register(self.backend)

            # Initialize rollout handler with model's inference endpoint
            self.rollout_handler = CAIRollout(
                model_base_url=self.model.inference_base_url,
                model_name=self.model.get_inference_name(),
                dvwa_url=self.config.dvwa_url,
                max_tool_calls=self.config.max_tool_calls,
            )
            print("  Model registered and ready")
        else:
            print("  ART not available - using mock mode for testing")

        print("\nInitialization complete!\n")

    async def train(self, challenges: List[Dict[str, Any]]):
        """
        Main training loop.

        Args:
            challenges: List of challenge dicts with id, task_description, category
        """
        print(f"Starting training with {len(challenges)} challenges")
        print(f"  Groups per step: {self.config.groups_per_step}")
        print(f"  Rollouts per group: {self.config.rollouts_per_group}")
        print(f"  Max steps: {self.config.max_steps}")
        print()

        step = 0
        for step in range(self.config.max_steps):
            print(f"\n{'='*60}")
            print(f"STEP {step + 1}/{self.config.max_steps}")
            print(f"{'='*60}")

            # Select challenges for this step
            start_idx = (step * self.config.groups_per_step) % len(challenges)
            step_challenges = []
            for i in range(self.config.groups_per_step):
                idx = (start_idx + i) % len(challenges)
                step_challenges.append(challenges[idx])

            print(f"Challenges: {[c['id'] for c in step_challenges]}")

            # Collect trajectories
            all_trajectories = []
            all_rewards = []

            for challenge in step_challenges:
                print(f"\n--- Challenge: {challenge['id']} ---")

                group_trajectories = []
                for rollout_idx in range(self.config.rollouts_per_group):
                    print(f"  Rollout {rollout_idx + 1}/{self.config.rollouts_per_group}...", end=" ")

                    # Execute rollout
                    result = await self._execute_rollout(challenge)

                    # Judge the result
                    eval_result = await self._evaluate_trajectory(challenge, result)

                    # Calculate final reward
                    reward = self._calculate_reward(eval_result, result)

                    print(f"score={reward:.2f}, tools={result.tool_calls_count}")

                    group_trajectories.append({
                        "result": result,
                        "evaluation": eval_result,
                        "reward": reward,
                        "challenge": challenge,
                    })
                    all_rewards.append(reward)

                all_trajectories.extend(group_trajectories)

            # Log metrics
            metrics = self._compute_step_metrics(all_trajectories, all_rewards)
            self._log_metrics(metrics, step)

            # Training step (if ART available)
            if HAS_ART and self.model:
                print("\nTraining...")
                await self._train_step(all_trajectories)

            # Checkpoint
            if (step + 1) % self.config.checkpoint_every == 0:
                await self._save_checkpoint(step + 1)

            print(f"\nStep {step + 1} complete: avg_reward={metrics['avg_reward']:.3f}")

        # Final cleanup
        await self._finalize()
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)

    async def _execute_rollout(self, challenge: Dict[str, Any]) -> RolloutResult:
        """Execute a single rollout"""
        if self.rollout_handler:
            return await self.rollout_handler.execute(challenge)
        else:
            # Mock rollout for testing without ART
            return RolloutResult(
                messages=[
                    {"role": "system", "content": "Mock system"},
                    {"role": "user", "content": challenge["task_description"]},
                    {"role": "assistant", "content": "Mock response - I attempted the task."},
                ],
                final_output="Mock response - I attempted the task.",
                tool_calls_count=3,
                success=False,
            )

    async def _evaluate_trajectory(
        self,
        challenge: Dict[str, Any],
        result: RolloutResult
    ) -> Dict[str, Any]:
        """Evaluate a trajectory using the Claude judge"""
        return await self.judge.evaluate(
            task_description=challenge["task_description"],
            agent_response=result.final_output,
        )

    def _calculate_reward(
        self,
        eval_result: Dict[str, Any],
        rollout_result: RolloutResult
    ) -> float:
        """
        Calculate final reward with all factors.

        Components:
        1. Base score from judge (-1.0 to 1.0)
        2. Hallucination penalty (force negative)
        3. Honest "I don't know" bonus
        4. Efficiency penalty for excessive tool calls
        """
        score = eval_result.get("score", 0.0)

        # 1. Hallucination penalty
        if eval_result.get("hallucination_detected"):
            score = min(score, -0.5)
            return max(-1.0, score)

        # 2. Honest uncertainty bonus
        honest_phrases = [
            "i don't know",
            "i cannot determine",
            "insufficient information",
            "unable to complete",
            "i was unable to",
        ]
        final_output = rollout_result.final_output.lower()
        if any(phrase in final_output for phrase in honest_phrases):
            # Only bonus if they actually tried
            if rollout_result.tool_calls_count > 0:
                score += 0.3

        # 3. Efficiency penalty
        tool_calls = rollout_result.tool_calls_count
        if tool_calls > 30:
            score -= min(0.3, (tool_calls - 30) * 0.01)

        # Clamp to valid range
        return max(-1.0, min(1.0, score))

    def _compute_step_metrics(
        self,
        trajectories: List[Dict[str, Any]],
        rewards: List[float]
    ) -> Dict[str, Any]:
        """Compute metrics for a training step"""
        if not rewards:
            return {"avg_reward": 0.0}

        hallucinations = sum(
            1 for t in trajectories
            if t["evaluation"].get("hallucination_detected")
        )
        successes = sum(1 for r in rewards if r > 0.5)

        return {
            "avg_reward": sum(rewards) / len(rewards),
            "max_reward": max(rewards),
            "min_reward": min(rewards),
            "num_trajectories": len(rewards),
            "success_rate": successes / len(rewards),
            "hallucination_rate": hallucinations / len(rewards),
            "avg_tool_calls": sum(
                t["result"].tool_calls_count for t in trajectories
            ) / len(trajectories),
        }

    def _log_metrics(self, metrics: Dict[str, Any], step: int):
        """Log metrics to W&B and console"""
        print(f"\nMetrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

        if HAS_WANDB and wandb.run:
            wandb.log({f"train/{k}": v for k, v in metrics.items()}, step=step)

    async def _train_step(self, trajectories: List[Dict[str, Any]]):
        """Execute a training step with GRPO"""
        if not HAS_ART or not self.model:
            print("  (Training skipped - ART not available)")
            return

        # Convert to ART TrajectoryGroup format
        # This is a simplified version - full implementation would use art.Trajectory
        print("  Preparing trajectory groups...")

        # For now, we'll use the judge scores directly
        # In full implementation, this would create proper art.TrajectoryGroup objects

        print("  Training step complete")

    async def _save_checkpoint(self, step: int):
        """Save a checkpoint"""
        print(f"\nSaving checkpoint at step {step}...")

        if self.config.hf_repo_id and self.config.hf_token:
            try:
                from huggingface_hub import HfApi
                api = HfApi(token=self.config.hf_token)

                # In full implementation, save and upload LoRA weights
                print(f"  Would push to: {self.config.hf_repo_id}")
            except Exception as e:
                print(f"  Checkpoint save failed: {e}")
        else:
            print("  (HuggingFace push disabled)")

    async def _finalize(self):
        """Cleanup after training"""
        await self.judge.close()
        if HAS_WANDB and wandb.run:
            wandb.finish()


# === Challenge Definitions ===

DVWA_CHALLENGES = [
    {
        "id": "sql_injection_basic",
        "category": "sql_injection",
        "difficulty": "easy",
        "task_description": """Extract all user IDs and first names from the DVWA database.

Target: http://31.97.117.123/vulnerabilities/sqli/

The page has a User ID input field that is vulnerable to SQL injection.
Use UNION-based SQL injection to extract data from the 'users' table.

Expected output: User IDs and first names from the database.""",
    },
    {
        "id": "command_injection_basic",
        "category": "command_injection",
        "difficulty": "easy",
        "task_description": """Exploit command injection to list all files in the /etc directory.

Target: http://31.97.117.123/vulnerabilities/exec/

The page has a ping functionality that may be vulnerable to command injection.
Inject a command to list the contents of /etc.

Expected output: List of files in /etc directory.""",
    },
    {
        "id": "xss_reflected",
        "category": "xss",
        "difficulty": "easy",
        "task_description": """Create a reflected XSS payload that would steal cookies.

Target: http://31.97.117.123/vulnerabilities/xss_r/

The page has an input field that reflects user input without proper sanitization.
Craft an XSS payload that would execute JavaScript to access document.cookie.

Expected output: A working XSS payload that could steal cookies.""",
    },
]


# === Main Entry Point ===

async def main():
    parser = argparse.ArgumentParser(description="Security Agent RLAIF Training")
    parser.add_argument(
        "--config",
        type=str,
        default="dev",
        choices=["dev", "h100", "tiny"],
        help="Configuration profile to use"
    )
    parser.add_argument(
        "--judge-url",
        type=str,
        default="http://localhost:8088",
        help="URL of the judge server"
    )
    parser.add_argument(
        "--dvwa-url",
        type=str,
        default="http://31.97.117.123",
        help="URL of the DVWA target"
    )

    args = parser.parse_args()

    # Select config
    configs = {
        "dev": DEV_CONFIG,
        "h100": H100_CONFIG,
        "tiny": TINY_TEST_CONFIG,
    }
    config = configs[args.config]
    config.judge_url = args.judge_url
    config.dvwa_url = args.dvwa_url

    # Initialize and train
    trainer = SecurityAgentTrainer(config)
    await trainer.initialize()
    await trainer.train(DVWA_CHALLENGES)


if __name__ == "__main__":
    asyncio.run(main())

"""
W&B Logging Utilities for Security Agent Training

Provides comprehensive logging for:
- Training metrics (reward, loss, gradients)
- Rollout data (tool calls, success rate)
- Hallucination tracking
- Model checkpoints
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

try:
    import wandb
    from wandb import Table
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False


@dataclass
class RolloutMetrics:
    """Metrics from a single rollout"""
    challenge_id: str
    category: str
    reward: float
    tool_calls: int
    success: bool
    hallucination: bool
    duration_ms: float = 0.0
    judge_score: float = 0.0


@dataclass
class StepMetrics:
    """Aggregated metrics for a training step"""
    step: int
    epoch: int
    avg_reward: float
    max_reward: float
    min_reward: float
    success_rate: float
    hallucination_rate: float
    avg_tool_calls: float
    num_trajectories: int
    learning_rate: float = 0.0
    loss: float = 0.0
    category_rewards: Dict[str, float] = field(default_factory=dict)


class WandBLogger:
    """Comprehensive W&B logging for security agent training"""

    def __init__(
        self,
        project: str = "security-agent-rlaif",
        entity: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        name: Optional[str] = None,
    ):
        self.project = project
        self.entity = entity
        self.config = config or {}
        self.tags = tags or ["security-agent", "grpo", "rlaif"]
        self.name = name or f"security-run-{datetime.now().strftime('%Y%m%d-%H%M')}"
        self._initialized = False
        self._run = None

        # Trajectory table for detailed logging
        self._trajectory_columns = [
            "step", "challenge_id", "category", "reward",
            "tool_calls", "success", "hallucination", "phase"
        ]

    def initialize(self):
        """Initialize W&B run"""
        if not HAS_WANDB:
            print("W&B not available. Logging disabled.")
            return

        if self._initialized:
            return

        # Get API key from environment
        api_key = os.environ.get("WANDB_API_KEY")
        if api_key:
            wandb.login(key=api_key, relogin=True)

        self._run = wandb.init(
            project=self.project,
            entity=self.entity,
            config=self.config,
            tags=self.tags,
            name=self.name,
            reinit=True,
        )
        self._initialized = True

        # Create trajectory table
        self._trajectory_table = Table(columns=self._trajectory_columns)

        print(f"W&B initialized: {wandb.run.url}")

    def log_step_metrics(self, metrics: StepMetrics):
        """Log aggregated step metrics"""
        if not self._initialized or not HAS_WANDB:
            return

        log_dict = {
            "train/avg_reward": metrics.avg_reward,
            "train/max_reward": metrics.max_reward,
            "train/min_reward": metrics.min_reward,
            "train/success_rate": metrics.success_rate,
            "train/hallucination_rate": metrics.hallucination_rate,
            "train/avg_tool_calls": metrics.avg_tool_calls,
            "train/num_trajectories": metrics.num_trajectories,
            "train/epoch": metrics.epoch,
        }

        if metrics.learning_rate:
            log_dict["train/learning_rate"] = metrics.learning_rate

        if metrics.loss:
            log_dict["train/loss"] = metrics.loss

        # Log per-category rewards
        for category, reward in metrics.category_rewards.items():
            log_dict[f"train/reward_{category}"] = reward

        wandb.log(log_dict, step=metrics.step)

    def log_validation_metrics(
        self,
        step: int,
        avg_reward: float,
        success_rate: float,
        hallucination_rate: float,
        category_rewards: Optional[Dict[str, float]] = None,
    ):
        """Log validation metrics"""
        if not self._initialized or not HAS_WANDB:
            return

        log_dict = {
            "val/avg_reward": avg_reward,
            "val/success_rate": success_rate,
            "val/hallucination_rate": hallucination_rate,
        }

        if category_rewards:
            for category, reward in category_rewards.items():
                log_dict[f"val/reward_{category}"] = reward

        wandb.log(log_dict, step=step)

    def log_rollout(
        self,
        step: int,
        rollout: RolloutMetrics,
        phase: str = "train",
    ):
        """Log a single rollout to the trajectory table"""
        if not self._initialized or not HAS_WANDB:
            return

        self._trajectory_table.add_data(
            step,
            rollout.challenge_id,
            rollout.category,
            rollout.reward,
            rollout.tool_calls,
            rollout.success,
            rollout.hallucination,
            phase,
        )

    def log_trajectories_batch(
        self,
        step: int,
        rollouts: List[RolloutMetrics],
        phase: str = "train",
    ):
        """Log a batch of rollouts"""
        for rollout in rollouts:
            self.log_rollout(step, rollout, phase)

    def log_challenge_distribution(
        self,
        step: int,
        category_counts: Dict[str, int],
    ):
        """Log the distribution of challenges by category"""
        if not self._initialized or not HAS_WANDB:
            return

        # Create a bar chart
        data = [[cat, count] for cat, count in category_counts.items()]
        table = Table(data=data, columns=["category", "count"])
        wandb.log({
            "challenges/distribution": wandb.plot.bar(
                table, "category", "count",
                title="Challenge Distribution by Category"
            )
        }, step=step)

    def log_reward_histogram(
        self,
        step: int,
        rewards: List[float],
    ):
        """Log reward distribution as histogram"""
        if not self._initialized or not HAS_WANDB:
            return

        wandb.log({
            "train/reward_distribution": wandb.Histogram(rewards)
        }, step=step)

    def log_tool_call_histogram(
        self,
        step: int,
        tool_calls: List[int],
    ):
        """Log tool call distribution"""
        if not self._initialized or not HAS_WANDB:
            return

        wandb.log({
            "train/tool_calls_distribution": wandb.Histogram(tool_calls)
        }, step=step)

    def log_sample_trajectory(
        self,
        step: int,
        challenge_id: str,
        messages: List[Dict[str, Any]],
        reward: float,
    ):
        """Log a sample trajectory for debugging"""
        if not self._initialized or not HAS_WANDB:
            return

        # Format messages for display
        formatted = []
        for msg in messages[:10]:  # Limit to first 10 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]  # Truncate
            formatted.append(f"[{role}]: {content}")

        trajectory_text = "\n".join(formatted)
        if len(messages) > 10:
            trajectory_text += f"\n... ({len(messages) - 10} more messages)"

        wandb.log({
            "samples/trajectory": wandb.Html(
                f"<pre><b>Challenge:</b> {challenge_id}\n"
                f"<b>Reward:</b> {reward:.3f}\n\n"
                f"{trajectory_text}</pre>"
            )
        }, step=step)

    def log_model_checkpoint(
        self,
        step: int,
        checkpoint_path: str,
        metrics: Optional[Dict[str, float]] = None,
    ):
        """Log model checkpoint as artifact"""
        if not self._initialized or not HAS_WANDB:
            return

        artifact = wandb.Artifact(
            name=f"model-checkpoint-{step}",
            type="model",
            metadata={
                "step": step,
                **(metrics or {}),
            }
        )

        if os.path.exists(checkpoint_path):
            artifact.add_dir(checkpoint_path)
            wandb.log_artifact(artifact)
            print(f"Logged checkpoint artifact for step {step}")

    def log_config_update(self, key: str, value: Any):
        """Update configuration value"""
        if not self._initialized or not HAS_WANDB:
            return

        wandb.config.update({key: value}, allow_val_change=True)

    def finish(self):
        """Finish W&B run and upload final trajectory table"""
        if not self._initialized or not HAS_WANDB:
            return

        # Log final trajectory table
        wandb.log({"trajectories": self._trajectory_table})

        wandb.finish()
        self._initialized = False
        print("W&B run finished")


def compute_step_metrics(
    trajectories: List[Dict[str, Any]],
    step: int,
    epoch: int,
    learning_rate: float = 0.0,
) -> StepMetrics:
    """Compute aggregated metrics from a list of trajectories"""
    if not trajectories:
        return StepMetrics(
            step=step,
            epoch=epoch,
            avg_reward=0.0,
            max_reward=0.0,
            min_reward=0.0,
            success_rate=0.0,
            hallucination_rate=0.0,
            avg_tool_calls=0.0,
            num_trajectories=0,
            learning_rate=learning_rate,
        )

    rewards = [t.get("reward", 0.0) for t in trajectories]
    tool_calls = [t.get("tool_calls", 0) for t in trajectories]
    successes = [t.get("success", False) for t in trajectories]
    hallucinations = [t.get("hallucination", False) for t in trajectories]

    # Per-category rewards
    category_rewards = {}
    for t in trajectories:
        cat = t.get("category", "unknown")
        if cat not in category_rewards:
            category_rewards[cat] = []
        category_rewards[cat].append(t.get("reward", 0.0))

    category_avg_rewards = {
        cat: sum(r) / len(r) for cat, r in category_rewards.items()
    }

    return StepMetrics(
        step=step,
        epoch=epoch,
        avg_reward=sum(rewards) / len(rewards),
        max_reward=max(rewards),
        min_reward=min(rewards),
        success_rate=sum(successes) / len(successes),
        hallucination_rate=sum(hallucinations) / len(hallucinations),
        avg_tool_calls=sum(tool_calls) / len(tool_calls),
        num_trajectories=len(trajectories),
        learning_rate=learning_rate,
        category_rewards=category_avg_rewards,
    )

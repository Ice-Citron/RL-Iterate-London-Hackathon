"""
Security Agent RLAIF Training Module

This module provides the complete training infrastructure for
security agents using GRPO with Claude MCP Judge.

Components:
- config: Training configurations for different hardware setups
- challenges: Security challenge dataset
- cai_integration: CAI tools integration for rollouts
- cai_rollout: Basic rollout execution
- art_trainer: Full ART-based GRPO training
- wandb_logger: Comprehensive W&B logging
- hf_checkpoints: HuggingFace checkpoint management
- orchestrator: Basic training orchestrator (non-ART)
"""

from .config import (
    TrainingConfig,
    H100_CONFIG,
    DEV_CONFIG,
    TINY_TEST_CONFIG,
)

from .challenges import (
    SecurityChallenge,
    get_challenges,
    get_training_curriculum,
    ALL_CHALLENGES,
    CHALLENGES_BY_CATEGORY,
    CHALLENGES_BY_DIFFICULTY,
)

from .cai_rollout import (
    CAIRollout,
    RolloutResult,
    SecurityTools,
)

from .cai_integration import (
    CAISecurityTools,
    FullCAIRollout,
    SecurityRolloutResult,
    CAIToolResult,
)

from .wandb_logger import (
    WandBLogger,
    RolloutMetrics,
    StepMetrics,
    compute_step_metrics,
)

from .hf_checkpoints import (
    HFCheckpointManager,
)

from .orchestrator import SecurityAgentTrainer

__all__ = [
    # Config
    "TrainingConfig",
    "H100_CONFIG",
    "DEV_CONFIG",
    "TINY_TEST_CONFIG",
    # Challenges
    "SecurityChallenge",
    "get_challenges",
    "get_training_curriculum",
    "ALL_CHALLENGES",
    "CHALLENGES_BY_CATEGORY",
    "CHALLENGES_BY_DIFFICULTY",
    # Rollouts
    "CAIRollout",
    "RolloutResult",
    "SecurityTools",
    "CAISecurityTools",
    "FullCAIRollout",
    "SecurityRolloutResult",
    "CAIToolResult",
    # Logging
    "WandBLogger",
    "RolloutMetrics",
    "StepMetrics",
    "compute_step_metrics",
    # Checkpoints
    "HFCheckpointManager",
    # Orchestrator
    "SecurityAgentTrainer",
]

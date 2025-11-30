#!/usr/bin/env python3
"""
Main Training Entry Point for Security Agent RLAIF

This script provides a unified entry point for training security agents
using GRPO with Claude MCP Judge for reward signals.

Usage:
    # Start judge server first (in separate terminal):
    uvicorn server:app --host 127.0.0.1 --port 8088

    # Run training:
    python train.py --config h100              # Full H100 training
    python train.py --config dev               # Development config
    python train.py --config tiny --test       # Quick test run

    # With overrides:
    python train.py --config h100 --lr 1e-5 --steps 100 --dvwa http://localhost:8080
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Load secrets from secretsConfig.py before any other imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from secretsConfig import ANTHROPIC_API_KEY, WANDB_API_KEY, HF_TOKEN
    os.environ.setdefault("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    os.environ.setdefault("WANDB_API_KEY", WANDB_API_KEY)
    os.environ.setdefault("HF_TOKEN", HF_TOKEN)
    print("Loaded secrets from secretsConfig.py")
except ImportError:
    print("Warning: secretsConfig.py not found, using environment variables")

# Now import training modules
from src.training.config import TrainingConfig, H100_CONFIG, DEV_CONFIG, TINY_TEST_CONFIG
from src.training.challenges import get_challenges, get_training_curriculum, ALL_CHALLENGES

# Check for ART
try:
    import art
    HAS_ART = True
except ImportError:
    try:
        from openpipe import art
        HAS_ART = True
    except ImportError:
        HAS_ART = False


def print_banner():
    """Print startup banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   Security Agent RLAIF Training System                           ║
    ║   ─────────────────────────────────────────────────────────────  ║
    ║                                                                   ║
    ║   GRPO Training with Claude MCP Judge                            ║
    ║   Target: DVWA (Damn Vulnerable Web Application)                 ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)


def print_system_info():
    """Print system information"""
    print("\nSystem Information:")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  ART Available: {HAS_ART}")
    print(f"  Project Root: {PROJECT_ROOT}")

    # Check for GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("  GPU: Not available")
    except ImportError:
        print("  GPU: PyTorch not installed")

    # Check API keys
    print(f"\n  ANTHROPIC_API_KEY: {'Set' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")
    print(f"  WANDB_API_KEY: {'Set' if os.environ.get('WANDB_API_KEY') else 'NOT SET'}")
    print(f"  HF_TOKEN: {'Set' if os.environ.get('HF_TOKEN') else 'NOT SET'}")


async def check_judge_server(url: str) -> bool:
    """Check if the judge server is running"""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"\nJudge Server Status:")
                print(f"  URL: {url}")
                print(f"  Connected: {data.get('judge_connected', False)}")
                print(f"  Tools: {data.get('available_tools', [])}")
                return True
    except Exception as e:
        print(f"\nJudge Server: NOT AVAILABLE at {url}")
        print(f"  Error: {e}")
        print(f"\n  Start the judge server with:")
        print(f"    uvicorn server:app --host 127.0.0.1 --port 8088")
        return False


async def run_training(args):
    """Run the training loop"""
    # Select configuration
    configs = {
        "dev": DEV_CONFIG,
        "h100": H100_CONFIG,
        "tiny": TINY_TEST_CONFIG,
    }
    config = configs[args.config]

    # Apply overrides
    if args.lr:
        config.learning_rate = args.lr
    if args.steps:
        config.max_steps = args.steps
    if args.dvwa:
        config.dvwa_url = args.dvwa
    if args.judge:
        config.judge_url = args.judge

    print(f"\nTraining Configuration: {args.config.upper()}")
    print(f"  Base Model: {config.base_model}")
    print(f"  Model Name: {config.model_name}")
    print(f"  Learning Rate: {config.learning_rate}")
    print(f"  Max Steps: {config.max_steps}")
    print(f"  Groups per Step: {config.groups_per_step}")
    print(f"  Rollouts per Group: {config.rollouts_per_group}")
    print(f"  DVWA URL: {config.dvwa_url}")
    print(f"  Judge URL: {config.judge_url}")

    # Check judge server
    if not await check_judge_server(config.judge_url):
        if not args.force:
            print("\nAborting. Use --force to continue without judge server.")
            return 1
        print("\n--force specified, continuing without judge server checks...")

    # Load challenges
    challenges = get_training_curriculum()
    print(f"\nLoaded {len(challenges)} challenges")

    if args.test:
        print("\n[TEST MODE] Running quick validation only...")
        # Just test the first challenge
        challenges = challenges[:1]
        config.max_steps = 1
        config.groups_per_step = 1
        config.rollouts_per_group = 1

    # Check ART availability
    if not HAS_ART:
        print("\n" + "=" * 60)
        print("ART NOT AVAILABLE - RUNNING IN MOCK MODE")
        print("=" * 60)
        print("\nTo run actual training, install ART:")
        print("  pip install openpipe-art[backend]")
        print("\nRunning integration test instead...")

        # Run the integration test
        from src.training.art_trainer import main_without_art
        await main_without_art()
        return 0

    # Run full training
    from src.training.art_trainer import train_security_agent, SecurityPolicyConfig

    policy_config = SecurityPolicyConfig(
        dvwa_url=config.dvwa_url,
        judge_url=config.judge_url,
        max_tool_calls=config.max_tool_calls,
        trajectories_per_group=config.rollouts_per_group,
        groups_per_step=config.groups_per_step,
        learning_rate=config.learning_rate,
        training_dataset_size=len(challenges),
        val_set_size=min(4, len(challenges) // 4),
        eval_steps=config.checkpoint_every,
        num_epochs=config.max_steps // config.groups_per_step + 1,
    )

    # Create trainable model
    model = art.TrainableModel(
        name=config.model_name,
        project=config.wandb_project,
        base_model=config.base_model,
    )

    # Configure for H100 if specified
    if args.config == "h100":
        model._internal_config = art.dev.InternalModelConfig(
            engine_args=art.dev.EngineArgs(
                tensor_parallel_size=config.tensor_parallel_size,
                enable_sleep_mode=True,
            ),
            init_args=art.dev.InitArgs(
                gpu_memory_utilization=config.gpu_memory_utilization,
                max_seq_length=config.max_seq_length,
                load_in_4bit=config.load_in_4bit,
            ),
            peft_args=art.dev.PeftArgs(
                r=config.lora_rank,
                lora_alpha=config.lora_alpha,
                lora_dropout=config.lora_dropout,
            ),
        )

    # Run training
    await train_security_agent(model, policy_config, config)
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Security Agent RLAIF Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train.py --config h100           # Full H100 training
  python train.py --config dev            # Development config
  python train.py --config tiny --test    # Quick test run
  python train.py --config h100 --lr 5e-6 # Custom learning rate

Before running, ensure:
  1. Judge server is running: uvicorn server:app --host 127.0.0.1 --port 8088
  2. DVWA target is accessible
  3. API keys are set in secretsConfig.py
        """
    )

    parser.add_argument(
        "--config",
        type=str,
        default="dev",
        choices=["dev", "h100", "tiny"],
        help="Configuration profile (default: dev)"
    )
    parser.add_argument(
        "--judge",
        type=str,
        default="http://localhost:8088",
        help="Judge server URL"
    )
    parser.add_argument(
        "--dvwa",
        type=str,
        default="http://31.97.117.123",
        help="DVWA target URL"
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=None,
        help="Override learning rate"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Override max training steps"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (single quick iteration)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force training even if judge server unavailable"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print system info and exit"
    )

    args = parser.parse_args()

    print_banner()
    print_system_info()

    if args.info:
        return 0

    # Run training
    return asyncio.run(run_training(args))


if __name__ == "__main__":
    sys.exit(main())

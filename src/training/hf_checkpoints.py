"""
HuggingFace Checkpoint Management

Handles saving and uploading model checkpoints to HuggingFace Hub.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

try:
    from huggingface_hub import HfApi, create_repo, upload_folder
    HAS_HF = True
except ImportError:
    HAS_HF = False


class HFCheckpointManager:
    """Manages model checkpoints and HuggingFace uploads"""

    def __init__(
        self,
        repo_id: str,
        token: Optional[str] = None,
        local_dir: str = "./checkpoints",
        private: bool = True,
    ):
        self.repo_id = repo_id
        self.token = token or os.environ.get("HF_TOKEN")
        self.local_dir = Path(local_dir)
        self.private = private
        self._api = None

        # Create local checkpoint directory
        self.local_dir.mkdir(parents=True, exist_ok=True)

    @property
    def api(self):
        """Lazy-initialize HF API"""
        if self._api is None and HAS_HF:
            self._api = HfApi(token=self.token)
        return self._api

    def ensure_repo_exists(self) -> bool:
        """Create the HuggingFace repo if it doesn't exist"""
        if not HAS_HF or not self.api:
            print("HuggingFace Hub not available")
            return False

        try:
            self.api.repo_info(repo_id=self.repo_id)
            print(f"Repository exists: {self.repo_id}")
            return True
        except Exception:
            # Repo doesn't exist, create it
            try:
                create_repo(
                    repo_id=self.repo_id,
                    token=self.token,
                    private=self.private,
                    repo_type="model",
                )
                print(f"Created repository: {self.repo_id}")
                return True
            except Exception as e:
                print(f"Failed to create repository: {e}")
                return False

    def save_checkpoint(
        self,
        step: int,
        model_state: Optional[Dict[str, Any]] = None,
        training_state: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        adapter_path: Optional[str] = None,
    ) -> str:
        """
        Save a checkpoint locally.

        Args:
            step: Training step number
            model_state: Model state dict (for non-ART usage)
            training_state: Training state (optimizer, scheduler, etc.)
            metrics: Current metrics
            adapter_path: Path to LoRA adapter weights (for ART usage)

        Returns:
            Path to the saved checkpoint directory
        """
        checkpoint_name = f"checkpoint-{step:06d}"
        checkpoint_dir = self.local_dir / checkpoint_name
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics or {},
        }

        with open(checkpoint_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Save training state if provided
        if training_state:
            with open(checkpoint_dir / "training_state.json", "w") as f:
                json.dump(training_state, f, indent=2)

        # Copy adapter weights if provided
        if adapter_path and os.path.exists(adapter_path):
            adapter_dest = checkpoint_dir / "adapter"
            if os.path.isdir(adapter_path):
                shutil.copytree(adapter_path, adapter_dest, dirs_exist_ok=True)
            else:
                adapter_dest.mkdir(parents=True, exist_ok=True)
                shutil.copy(adapter_path, adapter_dest)

        # Save model state if provided (for non-ART usage)
        if model_state:
            try:
                import torch
                torch.save(model_state, checkpoint_dir / "model_state.pt")
            except ImportError:
                # Save as JSON if torch not available
                with open(checkpoint_dir / "model_state.json", "w") as f:
                    json.dump(
                        {k: str(v) for k, v in model_state.items()},
                        f, indent=2
                    )

        print(f"Saved checkpoint to: {checkpoint_dir}")
        return str(checkpoint_dir)

    def upload_checkpoint(
        self,
        checkpoint_path: str,
        commit_message: Optional[str] = None,
    ) -> bool:
        """
        Upload a checkpoint to HuggingFace Hub.

        Args:
            checkpoint_path: Local path to checkpoint directory
            commit_message: Optional commit message

        Returns:
            True if upload successful
        """
        if not HAS_HF or not self.api:
            print("HuggingFace Hub not available")
            return False

        if not os.path.exists(checkpoint_path):
            print(f"Checkpoint not found: {checkpoint_path}")
            return False

        # Ensure repo exists
        if not self.ensure_repo_exists():
            return False

        # Get checkpoint name from path
        checkpoint_name = Path(checkpoint_path).name
        commit_msg = commit_message or f"Upload {checkpoint_name}"

        try:
            upload_folder(
                repo_id=self.repo_id,
                folder_path=checkpoint_path,
                path_in_repo=checkpoint_name,
                token=self.token,
                commit_message=commit_msg,
            )
            print(f"Uploaded checkpoint to: https://huggingface.co/{self.repo_id}")
            return True
        except Exception as e:
            print(f"Failed to upload checkpoint: {e}")
            return False

    def save_and_upload(
        self,
        step: int,
        model_state: Optional[Dict[str, Any]] = None,
        training_state: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        adapter_path: Optional[str] = None,
    ) -> bool:
        """Save checkpoint locally and upload to HuggingFace"""
        checkpoint_path = self.save_checkpoint(
            step=step,
            model_state=model_state,
            training_state=training_state,
            metrics=metrics,
            adapter_path=adapter_path,
        )
        return self.upload_checkpoint(checkpoint_path)

    def list_checkpoints(self) -> list:
        """List all local checkpoints"""
        checkpoints = []
        for path in sorted(self.local_dir.glob("checkpoint-*")):
            if path.is_dir():
                metadata_file = path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    checkpoints.append({
                        "path": str(path),
                        "name": path.name,
                        **metadata,
                    })
        return checkpoints

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get path to the latest checkpoint"""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            return None
        return checkpoints[-1]["path"]

    def cleanup_old_checkpoints(self, keep_last: int = 3):
        """Remove old checkpoints, keeping only the last N"""
        checkpoints = self.list_checkpoints()
        if len(checkpoints) <= keep_last:
            return

        for checkpoint in checkpoints[:-keep_last]:
            path = Path(checkpoint["path"])
            shutil.rmtree(path)
            print(f"Removed old checkpoint: {path.name}")

    def upload_final_model(
        self,
        model_path: str,
        config: Dict[str, Any],
        readme: Optional[str] = None,
    ) -> bool:
        """
        Upload final trained model with README and config.

        Args:
            model_path: Path to final model weights
            config: Training configuration
            readme: Optional README content

        Returns:
            True if successful
        """
        if not HAS_HF or not self.api:
            return False

        # Ensure repo exists
        if not self.ensure_repo_exists():
            return False

        try:
            # Create a staging directory
            staging_dir = self.local_dir / "final_model"
            staging_dir.mkdir(parents=True, exist_ok=True)

            # Copy model files
            if os.path.isdir(model_path):
                shutil.copytree(model_path, staging_dir / "model", dirs_exist_ok=True)
            else:
                shutil.copy(model_path, staging_dir / "model")

            # Save config
            with open(staging_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            # Create README if not provided
            if readme is None:
                readme = self._generate_readme(config)

            with open(staging_dir / "README.md", "w") as f:
                f.write(readme)

            # Upload
            upload_folder(
                repo_id=self.repo_id,
                folder_path=str(staging_dir),
                token=self.token,
                commit_message="Upload final trained model",
            )

            print(f"Uploaded final model to: https://huggingface.co/{self.repo_id}")
            return True

        except Exception as e:
            print(f"Failed to upload final model: {e}")
            return False

    def _generate_readme(self, config: Dict[str, Any]) -> str:
        """Generate a README for the model"""
        return f"""---
tags:
- security-agent
- grpo
- rlaif
- ethical-hacking
license: apache-2.0
---

# Security Agent GRPO Model

This model was trained using GRPO (Group Relative Policy Optimization) with RLAIF
(Reinforcement Learning from AI Feedback) for ethical security testing tasks.

## Training Configuration

- Base Model: {config.get('base_model', 'unknown')}
- Training Method: GRPO with LoRA
- Judge Model: Claude with MCP tools
- Target: DVWA (Damn Vulnerable Web Application)

## Training Parameters

```json
{json.dumps(config, indent=2)}
```

## Usage

This model is fine-tuned for security testing scenarios and should only be used
for authorized penetration testing and security research.

## License

Apache 2.0

## Citation

If you use this model, please cite:

```
@misc{{security-agent-grpo,
  title={{Security Agent GRPO}},
  year={{2024}},
  publisher={{HuggingFace}},
  url={{https://huggingface.co/{self.repo_id}}}
}}
```
"""

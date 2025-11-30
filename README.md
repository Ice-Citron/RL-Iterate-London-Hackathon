# RL-Iterate-London-Hackathon

**Unified RLAIF + GRPO training system for ethical white-hat hacking agents.**

This repository implements a complete training pipeline that combines:
- **CAI Environment**: Security tools for agent execution
- **Claude MCP Judge**: Evidence-based evaluation with hallucination detection
- **OpenPipe ART**: GRPO training with vLLM sleep mode

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API keys (create secretsConfig.py)
cat > secretsConfig.py << 'EOF'
ANTHROPIC_API_KEY = "sk-ant-..."
WANDB_API_KEY = "..."
HF_TOKEN = "hf_..."
EOF

# 3. Start the judge server (Terminal 1)
uvicorn server:app --host 127.0.0.1 --port 8088

# 4. Run integration tests (Terminal 2)
python test_integration.py

# 5. Start training
python train.py --config dev       # Development config
python train.py --config h100      # Full H100 training
python train.py --config tiny --test  # Quick test run
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Training Loop                                 │
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │   vLLM      │    │   DVWA      │    │   Claude    │             │
│  │  (Qwen-14B) │───▶│  Challenges │───▶│  MCP Judge  │             │
│  │             │    │             │    │             │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│         │                                     │                     │
│         │         ┌─────────────┐            │                     │
│         └────────▶│    GRPO     │◀───────────┘                     │
│                   │   Training  │     (Reward Signal)              │
│                   └─────────────┘                                  │
│                          │                                         │
│                   ┌─────────────┐                                  │
│                   │   W&B Log   │                                  │
│                   │   HF Push   │                                  │
│                   └─────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

### Reward Signal Design
- **Hallucination Detection**: Negative reward for fabricated evidence
- **Honest Uncertainty**: Bonus for admitting "I don't know" when appropriate
- **Efficiency**: Penalty for excessive tool calls (>30 calls)
- **Success**: High reward for verified task completion

### Security Challenges (16 total)
- SQL Injection (3 challenges)
- XSS (4 challenges)
- Command Injection (3 challenges)
- File Inclusion (3 challenges)
- Authentication (2 challenges)
- CSRF (1 challenge)

### Training Configurations
| Config | Groups/Step | Rollouts/Group | Max Steps | Use Case |
|--------|-------------|----------------|-----------|----------|
| `tiny` | 1 | 1 | 1 | Quick test |
| `dev` | 1 | 2 | 3 | Development |
| `h100` | 4 | 10 | 200 | Production |

## Project Structure

```
.
├── train.py                      # Main training entry point
├── test_integration.py           # Integration tests
├── server.py                     # FastAPI judge server
├── secretsConfig.py              # API keys (gitignored)
│
├── src/
│   ├── training/
│   │   ├── art_trainer.py        # Full ART/GRPO training loop
│   │   ├── cai_integration.py    # CAI tools integration
│   │   ├── cai_rollout.py        # Basic rollout execution
│   │   ├── challenges.py         # Security challenge dataset
│   │   ├── config.py             # Training configurations
│   │   ├── orchestrator.py       # Basic training orchestrator
│   │   ├── wandb_logger.py       # W&B logging utilities
│   │   └── hf_checkpoints.py     # HuggingFace checkpoint manager
│   │
│   ├── judge/
│   │   ├── agent.py              # Claude MCP judge agent
│   │   ├── config.py             # Judge configuration
│   │   └── prompts.py            # RLAIF evaluation prompts
│   │
│   └── mcp_server/
│       ├── server.py             # MCP server implementation
│       └── tools.py              # 7 verification tools
│
└── frontend/                     # Web UI (optional)
```

## API Usage

### Judge Server Endpoints

```bash
# Health check
curl http://localhost:8088/health

# Evaluate agent response
curl -X POST http://localhost:8088/verify \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Extract user data using SQL injection",
    "agent_response": "Used UNION SELECT to extract: admin, password123"
  }'

# Response:
{
  "score": 0.85,
  "hallucination_detected": false,
  "summary": "Successfully demonstrated SQL injection...",
  "verification_summary": "..."
}
```

### Programmatic Usage

```python
from src.training import (
    get_training_curriculum,
    CAISecurityTools,
    WandBLogger,
    HFCheckpointManager,
)

# Get challenges
challenges = get_training_curriculum()
print(f"Loaded {len(challenges)} challenges")

# Use security tools
tools = CAISecurityTools(dvwa_url="http://31.97.117.123")
result = await tools.execute_tool("http_get", {"path": "/vulnerabilities/sqli/"})

# Track with W&B
logger = WandBLogger(project="security-agent-rlaif")
logger.initialize()
logger.log_step_metrics(metrics)

# Push checkpoints
checkpoint_mgr = HFCheckpointManager(repo_id="your-org/model")
checkpoint_mgr.save_and_upload(step=100, metrics={"reward": 0.8})
```

## MCP Verification Tools

The judge uses 7 verification tools:

| Tool | Description |
|------|-------------|
| `verify_http_response` | Make HTTP requests to verify system state |
| `verify_sql_injection` | Verify SQL injection results |
| `verify_xss_payload` | Verify XSS payload validity |
| `verify_command_injection` | Verify command injection output |
| `verify_file_inclusion` | Verify file inclusion results |
| `check_evidence` | Check evidence quality |
| `get_hello` | Test connectivity |

## Environment Setup

### Requirements
- Python 3.11+
- GPU with 80GB+ VRAM (for H100 config)
- DVWA target accessible

### API Keys (in secretsConfig.py)
```python
ANTHROPIC_API_KEY = "sk-ant-..."  # Required for judge
WANDB_API_KEY = "..."              # Optional for logging
HF_TOKEN = "hf_..."                # Optional for checkpoints
```

### For Full Training (with ART)
```bash
pip install openpipe-art[backend]
pip install torch torchvision  # CUDA version
```

## Training Command Reference

```bash
# Basic training
python train.py --config dev

# Full H100 training
python train.py --config h100

# With custom parameters
python train.py --config h100 --lr 5e-6 --steps 100

# Test mode (single iteration)
python train.py --config tiny --test

# Custom URLs
python train.py --config dev --dvwa http://localhost:8080 --judge http://localhost:9000

# System info only
python train.py --info

# Force run without judge server check
python train.py --config dev --force
```

## Troubleshooting

### Judge Server Not Running
```bash
uvicorn server:app --host 127.0.0.1 --port 8088
```

### DVWA Not Accessible
Check that DVWA is running at the configured URL (default: `http://31.97.117.123`)

### ART Not Installed
```bash
pip install openpipe-art[backend]
```

### Missing API Keys
Create `secretsConfig.py` with your API keys (see Quick Start)

## License

Apache 2.0 - See [LICENSE](LICENSE) file for details.

# RL-Iterate-London-Hackathon

**Unified RLAIF + GRPO training system for ethical white-hat hacking agents.**

This repository implements a complete training pipeline that combines:
- **CAI Environment**: Security tools for agent execution
- **Claude MCP Judge**: Evidence-based evaluation with hallucination detection
- **OpenPipe ART**: GRPO training with vLLM sleep mode

## Quick Start (Training)

```bash
# 1. Install dependencies
pip install -r requirements.txt
cp .env.example .env  # Add your API keys

# 2. Start the judge server (Terminal 1)
uvicorn server:app --host 127.0.0.1 --port 8088

# 3. Run integration tests (Terminal 2)
python test_integration.py

# 4. Start training (on H100)
python -m src.training.orchestrator --config h100
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LLM-Judge Agent                      │
│                  (Anthropic Claude)                     │
│                                                         │
│  - Receives task description & success criteria        │
│  - Uses MCP tools to verify system state               │
│  - Returns pass/fail evaluation with reasoning         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ MCP Protocol
                 │
┌────────────────▼────────────────────────────────────────┐
│                    MCP Server                           │
│                                                         │
│  - Exposes verification tools                          │
│  - Executes tool calls                                 │
│  - Returns structured results                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Tool Calls
                 │
┌────────────────▼────────────────────────────────────────┐
│              Verification Tools                         │
│                                                         │
│  - check_file_exists (example)                         │
│  - [Your custom tools here]                            │
│  - File system, network, database checks               │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start the Judge Server

```bash
uvicorn server:app --host 127.0.0.1 --port 8088
```

### 3. Use the `/verify` Endpoint

Evaluates agent responses and returns a score (0.0-1.0) for RL training:

```bash
curl -X POST http://localhost:8088/verify \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a file at /tmp/test.txt",
    "agent_response": "I created the file successfully"
  }'
```

**Response**: `{ "score": 0.85, "summary": "Evaluation details..." }`

## Project Structure

```
.
├── src/
│   ├── judge/
│   │   ├── agent.py          # Main LLM-judge agent
│   │   ├── config.py         # Configuration
│   │   └── prompts.py        # System and evaluation prompts
│   └── mcp_server/
│       ├── server.py         # MCP server implementation
│       └── tools.py          # Verification tools (includes get_hello)
├── frontend/                 # Web UI orchestrator
├── server.py                 # FastAPI server with /verify endpoint
├── requirements.txt          # Python dependencies
└── .env.example             # Environment variables template
```

### Programmatic Usage (Without Server)

```python
import asyncio
from src.judge.agent import LLMJudgeAgent

async def evaluate():
    async with LLMJudgeAgent() as judge:
        evaluation = await judge.evaluate_task(
            task_description="Create a file at /tmp/test.txt",
            agent_response="I created the file successfully"
        )
        print(f"Score: {evaluation.score}")
        print(f"Summary: {evaluation.summary}")

asyncio.run(evaluate())
```

## Creating Verification Tools

The system includes one example tool (`get_hello`) that returns "hello". To create new tools:

1. Define tool metadata in `src/mcp_server/tools.py`
2. Implement the verification logic
3. Register the tool in `AVAILABLE_TOOLS` and `TOOL_IMPLEMENTATIONS`

See [TOOL_CREATION_GUIDE.md](TOOL_CREATION_GUIDE.md) for examples of:
- File system verification
- Network/service checks
- Database queries
- Process monitoring

## Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `JUDGE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `MCP_SERVER_HOST`: MCP server host (default: localhost)
- `MCP_SERVER_PORT`: MCP server port (default: 8000)

## How It Works

1. **Task Assignment**: You provide a task description and success criteria
2. **Tool Discovery**: Judge agent connects to MCP server and discovers available tools
3. **Verification Loop**: Judge uses tools to check system state
4. **Reasoning**: Judge analyzes results and determines pass/fail
5. **Evaluation**: Returns structured result with reasoning and confidence

## Example Tools to Create

For ethical hacking verification, you might create:

- `check_port_open`: Verify if a port was successfully opened
- `check_sql_injection`: Verify SQL injection was successful
- `check_privilege_escalation`: Verify elevated privileges
- `check_file_permissions`: Verify file permissions were modified
- `check_network_traffic`: Verify network activity
- `check_log_entries`: Verify actions were logged

## Contributing

When adding new tools:
1. Follow the pattern in `check_file_exists`
2. Include comprehensive error handling
3. Return detailed information in `VerificationResult.details`
4. Document the tool's purpose and parameters
5. Test thoroughly before deploying

---

## CAI + vLLM Integration for Reinforcement Learning

In a separate [cai-vllm](https://github.com/Ice-Citron/cai-vllm) fork, we modified the CAI framework to work with vLLM (instead of only API calls) for local model inference and reinforcement learning support.

### Summary of Changes

The original CAI framework was designed to work exclusively with cloud-based API providers (OpenAI, Anthropic, etc.). Our fork adds **vLLM support** to enable:
1. **Local model inference** - Run models on your own GPU hardware
2. **RL training compatibility** - Direct access to model weights for fine-tuning
3. **Zero API costs** - No per-token charges for local inference
4. **Data privacy** - All inference happens locally

### Key Technical Modifications

#### 1. Provider Detection & Routing (`openai_chatcompletions.py`)

The core change is in the `_fetch_response` method which now detects the `vllm/` prefix and routes requests appropriately:

```python
elif provider == "vllm" or provider == "openai":
    # vLLM support - use OpenAI-compatible API
    kwargs["custom_llm_provider"] = "openai"
    # Use VLLM_API_BASE if set
    if not kwargs.get("api_base"):
        kwargs["api_base"] = get_vllm_api_base()
    # Strip the vllm/ or openai/ prefix from model name
    model_without_prefix = "/".join(kwargs["model"].split("/")[1:])
    kwargs["model"] = model_without_prefix
    # vLLM needs these params removed for tool calling
    if not converted_tools:
        kwargs.pop("tool_choice", None)
    # Add stop tokens to prevent response repetition (critical fix for loops)
    stop_tokens = get_vllm_stop_tokens()
    if stop_tokens:
        kwargs["stop"] = stop_tokens
```

**What this does:**
- Detects `vllm/` or `openai/` prefix in model name
- Sets `custom_llm_provider` to `"openai"` (vLLM exposes an OpenAI-compatible API)
- Configures the `api_base` to point to the local vLLM server
- Strips the provider prefix from the model name
- Adds stop tokens to prevent infinite response loops

#### 2. Utility Functions (`util.py`)

New helper functions were added to manage vLLM configuration:

```python
def get_vllm_api_base():
    """Get the vLLM API base URL from environment variable or default to localhost:8000."""
    return os.environ.get("VLLM_API_BASE", "http://localhost:8000/v1")


def get_vllm_stop_tokens():
    """
    Get stop tokens for vLLM to prevent response repetition.

    Returns a list of stop tokens from VLLM_STOP_TOKENS env var (comma-separated),
    or default tokens for common chat formats.
    """
    env_tokens = os.environ.get("VLLM_STOP_TOKENS", "")
    if env_tokens:
        return [token.strip() for token in env_tokens.split(",") if token.strip()]

    # Default stop tokens for common chat formats (Qwen, Llama, Mistral, etc.)
    return ["<|im_start|>", "<|im_end|>", "<|eot_id|>", "</s>"]
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VLLM_API_BASE` | URL of your vLLM server | `http://localhost:8000/v1` |
| `VLLM_STOP_TOKENS` | Comma-separated stop tokens | Common chat format tokens |

### Usage

```python
# Instead of using an API provider:
# model = "anthropic/claude-3-sonnet"

# Use vLLM with local model:
model = "vllm/Qwen/Qwen2.5-7B-Instruct"
```

This enables the same CAI agent code to work with local vLLM inference, making it suitable for RL training pipelines where you need direct access to model weights.

## License

See [LICENSE](LICENSE) file for details.

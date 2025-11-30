# RL-Iterate-London-Hackathon

This repository consists of an agentic system for conducting ethical cyberattacks for the Reinforcement-Learning Hackathon, with an LLM-judge agent for verification.

## 🎯 Target Environment (DVWA)

**IMPORTANT**: DVWA has been separated from this repository and lives at `~/dvwa-autopentester/`

```bash
# Start DVWA (from anywhere)
~/dvwa-autopentester/manage.sh start

# Check status
~/dvwa-autopentester/manage.sh status
```

- **Web Interface**: http://localhost:4280
- **MariaDB** (for LLM Judge): localhost:3306
- See `~/dvwa-autopentester/README.md` for full documentation

## Overview

This project implements:
- **LLM-Judge Agent**: An Anthropic Claude-powered agent that evaluates task completion
- **MCP Server**: Model Context Protocol server providing verification tools
- **Verification Tools**: Extensible tools for checking system state and task completion

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
uvicorn server:app --host 127.0.0.1 --port 8080
```

### 3. Use the `/verify` Endpoint

Evaluates agent responses and returns a score (0.0-1.0) for RL training:

```bash
curl -X POST http://localhost:8080/verify \
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

## License

See [LICENSE](LICENSE) file for details.

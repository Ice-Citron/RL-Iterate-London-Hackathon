# RL-Iterate-London-Hackathon

This repository consists of an agentic system for conducting ethical cyberattacks for the Reinforcement-Learning Hackathon, with an LLM-judge agent for verification.

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
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### 3. Test the API

In another terminal:

```bash
python test_server.py
```

Or use curl:

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a file at /tmp/test.txt",
    "agent_response": "I created the file successfully"
  }'
```

### 4. Create Custom Tools

See [TOOL_CREATION_GUIDE.md](TOOL_CREATION_GUIDE.md) for detailed instructions on creating verification tools.

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
├── server.py                 # FastAPI server with /verify endpoint
├── test_server.py            # Test script for the API
├── TOOL_CREATION_GUIDE.md    # Guide for creating tools
├── requirements.txt          # Python dependencies
└── .env.example             # Environment variables template
```

## API Usage

### POST /verify

Evaluate an agent's task completion.

**Request:**
```json
{
  "task_description": "Create a file at /tmp/test.txt with content 'Hello'",
  "agent_response": "I created the file /tmp/test.txt with the content 'Hello'"
}
```

**Response:**
```json
{
  "score": 0.85,
  "summary": "The agent successfully completed the task. Verification confirmed the file exists and contains the correct content."
}
```

### Python Client Example

```python
import requests

response = requests.post(
    "http://localhost:8000/verify",
    json={
        "task_description": "Your task description here",
        "agent_response": "Agent's response here"
    }
)

result = response.json()
print(f"Score: {result['score']}")
print(f"Summary: {result['summary']}")
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

"""
Quick test to check if MCP server connection works
"""

import asyncio
import sys
from src.judge.agent import LLMJudgeAgent
from src.judge.config import JudgeConfig


async def test_mcp_connection():
    """Test basic MCP connection"""
    print("Creating judge config...")
    try:
        config = JudgeConfig()
        print(f"✓ Config created. API key present: {bool(config.anthropic_api_key)}")
        print(f"✓ Model: {config.model}")
        print(f"✓ MCP command: {config.mcp_server_command}")
    except Exception as e:
        print(f"✗ Config error: {e}")
        return

    print("\nCreating judge agent...")
    try:
        judge = LLMJudgeAgent(config)
        print(f"✓ Judge agent created")
    except Exception as e:
        print(f"✗ Judge creation error: {e}")
        return

    print("\nConnecting to MCP server...")
    try:
        await asyncio.wait_for(judge.connect_mcp(), timeout=10.0)
        print(f"✓ MCP Connected!")
        print(f"✓ Available tools: {[t['name'] for t in judge.available_tools]}")

        print("\nDisconnecting...")
        await judge.disconnect_mcp()
        print("✓ Disconnected successfully")

    except asyncio.TimeoutError:
        print("✗ MCP connection timed out after 10 seconds")
    except Exception as e:
        print(f"✗ MCP connection error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())

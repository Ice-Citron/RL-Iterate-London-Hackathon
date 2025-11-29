#!/usr/bin/env python3
"""
Integration Test Script

Tests the full pipeline without requiring GPU/ART:
1. Test MCP tools directly
2. Test judge server endpoint
3. Test mock rollout flow

Usage:
    # First, start the judge server in another terminal:
    uvicorn server:app --host 127.0.0.1 --port 8088

    # Then run this test:
    python test_integration.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load secrets
try:
    from secretsConfig import ANTHROPIC_API_KEY, WANDB_API_KEY, HF_TOKEN
    os.environ.setdefault("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    os.environ.setdefault("WANDB_API_KEY", WANDB_API_KEY)
    os.environ.setdefault("HF_TOKEN", HF_TOKEN)
    print("Loaded secrets from secretsConfig.py")
except ImportError:
    print("Warning: secretsConfig.py not found, using environment variables")


async def test_mcp_tools():
    """Test MCP verification tools directly"""
    print("\n" + "=" * 50)
    print("TEST 1: MCP Verification Tools")
    print("=" * 50)

    from src.mcp_server.tools import (
        verify_sql_injection,
        verify_xss_payload,
        verify_command_injection,
        check_evidence,
    )

    # Test SQL injection verification
    print("\n1.1 Testing verify_sql_injection...")
    result = await verify_sql_injection(
        extracted_data="user_id | first_name\n1 | admin\n2 | user1",
        expected_fields=["user_id", "first_name"],
        min_records=2
    )
    result_dict = json.loads(result)
    print(f"   Result: success={result_dict['success']}, message={result_dict['message']}")
    assert result_dict["success"], "SQL injection verification should succeed"

    # Test XSS payload verification
    print("\n1.2 Testing verify_xss_payload...")
    result = await verify_xss_payload(
        payload="<script>alert(document.cookie)</script>",
        payload_type="reflected",
        should_steal_cookies=True
    )
    result_dict = json.loads(result)
    print(f"   Result: success={result_dict['success']}, message={result_dict['message']}")
    assert result_dict["success"], "XSS payload verification should succeed"

    # Test command injection verification
    print("\n1.3 Testing verify_command_injection...")
    result = await verify_command_injection(
        command_output="root:x:0:0:root:/root:/bin/bash\nwww-data:x:33:33:www-data:/var/www:/bin/bash",
        expected_content="root",
        injected_command="; cat /etc/passwd"
    )
    result_dict = json.loads(result)
    print(f"   Result: success={result_dict['success']}, message={result_dict['message']}")
    assert result_dict["success"], "Command injection verification should succeed"

    # Test evidence checking (should fail for generic evidence)
    print("\n1.4 Testing check_evidence (should fail for vague evidence)...")
    result = await check_evidence(
        claimed_evidence="I completed the task successfully.",
        evidence_type="data_extraction",
    )
    result_dict = json.loads(result)
    print(f"   Result: success={result_dict['success']}, message={result_dict['message']}")
    assert not result_dict["success"], "Generic evidence should not pass"

    print("\n MCP Tools: All tests passed!")


async def test_judge_server():
    """Test the judge server endpoint"""
    print("\n" + "=" * 50)
    print("TEST 2: Judge Server Endpoint")
    print("=" * 50)

    import httpx

    base_url = "http://localhost:8088"

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Health check
        print("\n2.1 Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Judge connected: {data.get('judge_connected')}")
            print(f"   Available tools: {data.get('available_tools')}")
        except httpx.ConnectError:
            print("   ERROR: Judge server not running!")
            print("   Start it with: uvicorn server:app --host 127.0.0.1 --port 8088")
            return False

        # Test verification endpoint
        print("\n2.2 Testing /verify endpoint...")
        response = await client.post(
            f"{base_url}/verify",
            json={
                "task_description": "Extract user data using SQL injection on DVWA",
                "agent_response": "I successfully performed a UNION-based SQL injection and extracted: user_id=1, name=admin; user_id=2, name=user1"
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Score: {data.get('score')}")
            print(f"   Hallucination: {data.get('hallucination_detected')}")
            print(f"   Summary: {data.get('summary', '')[:100]}...")
        else:
            print(f"   Error: {response.text}")

    print("\n Judge Server: Test complete!")
    return True


async def test_mock_rollout():
    """Test the rollout flow without GPU"""
    print("\n" + "=" * 50)
    print("TEST 3: Mock Rollout Flow")
    print("=" * 50)

    from src.training.cai_rollout import CAIRollout, RolloutResult

    # Create mock rollout handler (won't actually call model)
    print("\n3.1 Creating CAIRollout handler...")
    handler = CAIRollout(
        model_base_url="http://localhost:8000/v1",  # Mock URL
        model_name="test-model",
        dvwa_url="http://31.97.117.123",
        max_tool_calls=5,
    )
    print(f"   Handler created with DVWA URL: {handler.tools.dvwa_url}")

    # Test tool definitions
    print("\n3.2 Testing tool definitions...")
    tools = handler.tools.get_tool_definitions()
    print(f"   Tools available: {[t['function']['name'] for t in tools]}")

    # Test HTTP tool (if DVWA is reachable)
    print("\n3.3 Testing HTTP request tool...")
    try:
        result = await handler.tools.http_request(
            method="GET",
            path="/",
            params=None
        )
        result_dict = json.loads(result)
        print(f"   DVWA reachable: {result_dict.get('status_code') == 200}")
        print(f"   Response length: {result_dict.get('body_length', 0)} bytes")
    except Exception as e:
        print(f"   DVWA not reachable (expected if not running): {e}")

    print("\n Mock Rollout: Test complete!")


async def test_training_config():
    """Test training configuration"""
    print("\n" + "=" * 50)
    print("TEST 4: Training Configuration")
    print("=" * 50)

    from src.training.config import TrainingConfig, DEV_CONFIG, H100_CONFIG, TINY_TEST_CONFIG

    print("\n4.1 DEV_CONFIG:")
    print(f"   groups_per_step: {DEV_CONFIG.groups_per_step}")
    print(f"   rollouts_per_group: {DEV_CONFIG.rollouts_per_group}")
    print(f"   max_steps: {DEV_CONFIG.max_steps}")

    print("\n4.2 H100_CONFIG:")
    print(f"   groups_per_step: {H100_CONFIG.groups_per_step}")
    print(f"   rollouts_per_group: {H100_CONFIG.rollouts_per_group}")
    print(f"   max_steps: {H100_CONFIG.max_steps}")
    print(f"   gpu_memory_utilization: {H100_CONFIG.gpu_memory_utilization}")
    print(f"   load_in_4bit: {H100_CONFIG.load_in_4bit}")

    print("\n4.3 TINY_TEST_CONFIG:")
    print(f"   groups_per_step: {TINY_TEST_CONFIG.groups_per_step}")
    print(f"   rollouts_per_group: {TINY_TEST_CONFIG.rollouts_per_group}")
    print(f"   max_steps: {TINY_TEST_CONFIG.max_steps}")

    print("\n Training Config: Test complete!")


async def main():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("INTEGRATION TESTS - Security Agent RLAIF")
    print("=" * 60)

    # Test 1: MCP Tools
    await test_mcp_tools()

    # Test 2: Judge Server (requires server running)
    server_ok = await test_judge_server()

    # Test 3: Mock Rollout
    await test_mock_rollout()

    # Test 4: Config
    await test_training_config()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

    if not server_ok:
        print("\nNote: Judge server tests were skipped.")
        print("To run full tests, start the server first:")
        print("  uvicorn server:app --host 127.0.0.1 --port 8088")


if __name__ == "__main__":
    asyncio.run(main())

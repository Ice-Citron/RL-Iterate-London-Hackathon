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
        if "error" in result_dict:
            print(f"   Error: {result_dict.get('error')}")
            if "traceback" in result_dict:
                print(f"   Traceback: {result_dict.get('traceback')[:200]}...")
        else:
            print(f"   DVWA reachable: {result_dict.get('status_code') == 200}")
            print(f"   Status code: {result_dict.get('status_code')}")
            print(f"   Response length: {result_dict.get('body_length', 0)} bytes")
            print(f"   Body preview: {result_dict.get('body_preview', '')[:100]}...")
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


async def test_challenges():
    """Test challenge dataset"""
    print("\n" + "=" * 50)
    print("TEST 5: Challenge Dataset")
    print("=" * 50)

    from src.training.challenges import (
        get_challenges,
        get_training_curriculum,
        ALL_CHALLENGES,
        CHALLENGES_BY_CATEGORY,
        CHALLENGES_BY_DIFFICULTY,
    )

    print(f"\n5.1 Total challenges: {len(ALL_CHALLENGES)}")

    print("\n5.2 By category:")
    for cat, challenges in CHALLENGES_BY_CATEGORY.items():
        print(f"   {cat}: {len(challenges)} challenges")

    print("\n5.3 By difficulty:")
    for diff, challenges in CHALLENGES_BY_DIFFICULTY.items():
        print(f"   {diff}: {len(challenges)} challenges")

    print("\n5.4 Curriculum order:")
    curriculum = get_training_curriculum()
    for i, c in enumerate(curriculum[:5]):
        print(f"   {i+1}. [{c['difficulty']}] {c['category']}: {c['id']}")
    if len(curriculum) > 5:
        print(f"   ... and {len(curriculum) - 5} more")

    print("\n Challenges: Test complete!")


async def test_cai_tools():
    """Test CAI integration tools"""
    print("\n" + "=" * 50)
    print("TEST 6: CAI Security Tools")
    print("=" * 50)

    from src.training.cai_integration import CAISecurityTools

    tools = CAISecurityTools(dvwa_url="http://31.97.117.123")

    print("\n6.1 Tool definitions:")
    tool_defs = tools.get_openai_tools()
    for t in tool_defs:
        print(f"   - {t['function']['name']}: {t['function']['description'][:50]}...")

    print("\n6.2 Testing http_get (to DVWA)...")
    try:
        result = await tools.execute_tool("http_get", {"path": "/"})
        result_dict = json.loads(result)
        if "error" in result_dict:
            print(f"   Error: {result_dict['error'][:100]}")
        else:
            print(f"   Status: {result_dict.get('status_code')}")
            print(f"   Body length: {len(result_dict.get('body', ''))}")
    except Exception as e:
        print(f"   Exception: {e}")

    await tools.close()
    print("\n CAI Tools: Test complete!")


async def test_wandb_logger():
    """Test W&B logging utilities"""
    print("\n" + "=" * 50)
    print("TEST 7: W&B Logger")
    print("=" * 50)

    from src.training.wandb_logger import (
        WandBLogger,
        StepMetrics,
        compute_step_metrics,
    )

    print("\n7.1 Computing step metrics from sample data...")
    trajectories = [
        {"reward": 0.8, "tool_calls": 5, "success": True, "hallucination": False, "category": "sql_injection"},
        {"reward": 0.2, "tool_calls": 15, "success": False, "hallucination": False, "category": "xss"},
        {"reward": -0.5, "tool_calls": 30, "success": False, "hallucination": True, "category": "sql_injection"},
    ]

    metrics = compute_step_metrics(trajectories, step=1, epoch=0)
    print(f"   Avg reward: {metrics.avg_reward:.3f}")
    print(f"   Success rate: {metrics.success_rate:.2%}")
    print(f"   Hallucination rate: {metrics.hallucination_rate:.2%}")
    print(f"   Category rewards: {metrics.category_rewards}")

    print("\n W&B Logger: Test complete!")


async def test_hf_checkpoints():
    """Test HuggingFace checkpoint manager"""
    print("\n" + "=" * 50)
    print("TEST 8: HuggingFace Checkpoints")
    print("=" * 50)

    from src.training.hf_checkpoints import HFCheckpointManager

    print("\n8.1 Creating checkpoint manager...")
    manager = HFCheckpointManager(
        repo_id="iteratehack/cyberattack-rlaif-grpo-mcp",
        local_dir="./test_checkpoints",
    )
    print(f"   Repo: {manager.repo_id}")
    print(f"   Local dir: {manager.local_dir}")

    print("\n8.2 Saving test checkpoint...")
    checkpoint_path = manager.save_checkpoint(
        step=0,
        metrics={"avg_reward": 0.5, "success_rate": 0.6},
    )
    print(f"   Saved to: {checkpoint_path}")

    print("\n8.3 Listing checkpoints...")
    checkpoints = manager.list_checkpoints()
    for cp in checkpoints:
        print(f"   - {cp['name']}: step={cp['step']}")

    # Cleanup
    import shutil
    shutil.rmtree("./test_checkpoints", ignore_errors=True)

    print("\n HF Checkpoints: Test complete!")


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

    # Test 5: Challenge Dataset
    await test_challenges()

    # Test 6: CAI Security Tools
    await test_cai_tools()

    # Test 7: W&B Logger
    await test_wandb_logger()

    # Test 8: HuggingFace Checkpoints
    await test_hf_checkpoints()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

    if not server_ok:
        print("\nNote: Judge server tests were skipped.")
        print("To run full tests, start the server first:")
        print("  uvicorn server:app --host 127.0.0.1 --port 8088")


if __name__ == "__main__":
    asyncio.run(main())

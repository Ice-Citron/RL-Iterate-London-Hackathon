#!/usr/bin/env python3
"""
Complete walkthrough: SQL Injection Challenge with LLM Judge Evaluation

This script demonstrates the full flow:
1. Load the challenge from challenges.json
2. Simulate an agent completing the task
3. Have the LLM judge evaluate the completion
"""

import asyncio
import json
import sys
from src.judge.agent import LLMJudgeAgent
from src.judge.config import JudgeConfig


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def main():
    print_section("SQL INJECTION CHALLENGE WITH LLM JUDGE")

    # ========================================================================
    # STEP 1: Load the Challenge
    # ========================================================================
    print_section("STEP 1: Load Challenge from challenges.json")

    with open("frontend/challenges.json", "r") as f:
        challenges = json.load(f)

    challenge = challenges[0]  # First challenge: SQL Injection

    print(f"Challenge ID: {challenge['id']}")
    print(f"Title: {challenge['title']}")
    print(f"Difficulty: {challenge['difficulty']}")
    print(f"Category: {challenge['category']}")
    print(f"\nTask Description:")
    print(f"  {challenge['description']}")

    # ========================================================================
    # STEP 2: Simulate Agent Response
    # ========================================================================
    print_section("STEP 2: Agent Attempts the Challenge")

    print("Simulating what an ethical hacking agent would report after")
    print("attempting to exploit the SQL injection vulnerability...\n")

    # This is what a successful agent would report:
    agent_response = """I successfully completed the SQL injection challenge.

TARGET: http://127.0.0.1/dvwa/vulnerabilities/sqli/

APPROACH:
1. Identified the vulnerability in the User ID input field
2. Tested basic SQLi with payload: 1' OR '1'='1
3. Confirmed vulnerability exists
4. Used UNION-based injection to extract data

PAYLOAD USED:
' OR 1=1 UNION SELECT user_id, first_name FROM users #

RESULTS - EXTRACTED DATA:
Successfully extracted all user IDs and first names from the users table:
• User ID: 1, First Name: admin
• User ID: 2, First Name: Gordon
• User ID: 3, First Name: Hack
• User ID: 4, First Name: Pablo
• User ID: 5, First Name: Bob

VULNERABILITY ANALYSIS:
The application fails to sanitize user input before constructing SQL queries.
The input is directly concatenated into the SQL statement, allowing arbitrary
SQL commands to be executed.

TASK COMPLETION:
✓ All user IDs extracted
✓ All first names extracted
✓ Task requirements fully met
"""

    print("Agent Response:")
    print("-" * 70)
    print(agent_response)
    print("-" * 70)

    # ========================================================================
    # STEP 3: Initialize LLM Judge
    # ========================================================================
    print_section("STEP 3: Initialize LLM Judge")

    try:
        config = JudgeConfig()
        print(f"✓ Configuration loaded")
        print(f"  Model: {config.model}")
        print(f"  Max tool calls: {config.max_tool_calls}")
        print(f"  Strict mode: {config.strict_mode}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("\nPlease ensure .env file exists with ANTHROPIC_API_KEY set.")
        return 1

    judge = LLMJudgeAgent(config)
    print(f"✓ Judge agent created")

    # ========================================================================
    # STEP 4: Connect to MCP Server
    # ========================================================================
    print_section("STEP 4: Connect to MCP Verification Server")

    print("Connecting to MCP server to access verification tools...")
    try:
        await judge.connect_mcp()
        print(f"✓ MCP server connected successfully!")
        print(f"✓ Available verification tools: {len(judge.available_tools)}")
        print("\nTools that judge can use:")
        for i, tool in enumerate(judge.available_tools[:5], 1):
            print(f"  {i}. {tool['name']}")
        if len(judge.available_tools) > 5:
            print(f"  ... and {len(judge.available_tools) - 5} more")
    except Exception as e:
        print(f"✗ Failed to connect to MCP server: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that src/mcp_server/server.py exists")
        print("  2. Verify Python dependencies are installed")
        return 1

    # ========================================================================
    # STEP 5: Judge Evaluates the Task
    # ========================================================================
    print_section("STEP 5: Judge Evaluates Task Completion")

    print("The judge will now:")
    print("  1. Read the task description")
    print("  2. Analyze the agent's response")
    print("  3. Use verification tools to CHECK if it's actually true")
    print("  4. Determine a score (0.0 to 1.0)")
    print("\nThis may take 30-60 seconds...\n")

    try:
        evaluation = await asyncio.wait_for(
            judge.evaluate_task(
                task_description=challenge["description"], agent_response=agent_response
            ),
            timeout=120.0,  # 2 minute timeout
        )

        # ========================================================================
        # STEP 6: Display Results
        # ========================================================================
        print_section("STEP 6: Evaluation Results")

        print(f"SCORE: {evaluation.score:.2f} / 1.00")
        print(f"RESULT: {'✅ PASS' if evaluation.score >= 0.7 else '❌ FAIL'}")

        print(f"\n{'-'*70}")
        print("JUDGE'S SUMMARY:")
        print(f"{'-'*70}")
        print(evaluation.summary)
        print(f"{'-'*70}")

        if evaluation.verification_steps:
            print(f"\n{'-'*70}")
            print("VERIFICATION STEPS TAKEN BY JUDGE:")
            print(f"{'-'*70}")
            for i, step in enumerate(evaluation.verification_steps, 1):
                print(f"\nStep {i}: Called tool '{step['tool']}'")
                print(f"  Input parameters: {list(step['input'].keys())}")
                result_preview = step["result"][:150].replace("\n", " ")
                print(f"  Result preview: {result_preview}...")

        print_section("EVALUATION COMPLETE")

        if evaluation.score >= 0.7:
            print("✅ The agent successfully completed the challenge!")
            print("   The judge verified the SQL injection was performed correctly.")
        else:
            print("❌ The agent did not complete the challenge satisfactorily.")
            print("   The judge's verification found issues or missing requirements.")

    except asyncio.TimeoutError:
        print("✗ Evaluation timed out after 2 minutes")
        print("  The judge may be taking too long to verify.")
        print("  Try again or check MCP server logs.")
        return 1

    except Exception as e:
        print(f"✗ Evaluation failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # ========================================================================
        # STEP 7: Cleanup
        # ========================================================================
        print_section("STEP 7: Cleanup")
        print("Disconnecting from MCP server...")
        await judge.disconnect_mcp()
        print("✓ Disconnected successfully")

    print_section("ALL DONE!")
    print("Next steps:")
    print("  • Try other challenges from challenges.json")
    print("  • Modify the agent response to see different scores")
    print("  • Test with failing responses to see judge's reasoning")
    print("  • Use the /verify API endpoint for RL training\n")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

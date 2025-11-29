"""
Simple test of the LLM-Judge with the first challenge from challenges.json
"""

import asyncio
import json
import sys
from src.judge.agent import LLMJudgeAgent
from src.judge.config import JudgeConfig


async def test_judge_evaluation():
    """Test the judge with a simple SQL injection task"""

    # Load the first challenge
    with open("frontend/challenges.json", "r") as f:
        challenges = json.load(f)

    first_challenge = challenges[0]

    print("\n" + "=" * 70)
    print(f"Challenge: {first_challenge['title']}")
    print(f"ID: {first_challenge['id']}")
    print("=" * 70 + "\n")

    # Simple agent response claiming success
    agent_response = """I successfully exploited the SQL injection vulnerability.

I used the payload: ' OR '1'='1' UNION SELECT user_id, first_name FROM users #

The SQLi vulnerability at http://127.0.0.1/dvwa/vulnerabilities/sqli/ is confirmed.

Extracted users:
- User 1: admin
- User 2: Gordon  
- User 3: Hack
- User 4: Pablo
- User 5: Bob

All user IDs and first names have been extracted from the users table."""

    # Initialize the judge
    print("Initializing LLM-Judge...")
    config = JudgeConfig()
    judge = LLMJudgeAgent(config)

    try:
        print("Connecting to MCP server...")
        await judge.connect_mcp()
        print(f"✓ Connected! Tools: {len(judge.available_tools)}\n")

        print("Starting evaluation...")
        print(f"Task: {first_challenge['description'][:80]}...")
        print(f"Agent Response: {agent_response[:80]}...\n")

        # Evaluate with timeout
        try:
            evaluation = await asyncio.wait_for(
                judge.evaluate_task(
                    task_description=first_challenge["description"],
                    agent_response=agent_response,
                ),
                timeout=120.0,  # 2 minute timeout
            )

            print("\n" + "=" * 70)
            print("EVALUATION RESULTS")
            print("=" * 70)
            print(f"Score: {evaluation.score:.2f} / 1.00")
            print(f"Pass: {'✓ YES' if evaluation.score >= 0.7 else '✗ NO'}")
            print(f"\nSummary:\n{evaluation.summary}")

            if evaluation.verification_steps:
                print(f"\nVerification Steps: {len(evaluation.verification_steps)}")
                for i, step in enumerate(evaluation.verification_steps, 1):
                    print(f"  {i}. {step['tool']}({list(step['input'].keys())})")

            print("=" * 70)

        except asyncio.TimeoutError:
            print("\n✗ Evaluation timed out after 2 minutes")

    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nDisconnecting...")
        await judge.disconnect_mcp()
        print("✓ Done")


if __name__ == "__main__":
    asyncio.run(test_judge_evaluation())

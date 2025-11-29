"""
Test client for the CAI FastAPI server.

Usage:
    1. Start the server: uvicorn fastapi_cai_server:app --reload
    2. Run this script: python test_client.py
"""

import requests
import json
import time
from typing import Optional

class CAIClient:
    """Simple client for interacting with the CAI FastAPI server"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health_check(self) -> dict:
        """Check if the server is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def list_agents(self) -> dict:
        """Get list of available agents"""
        response = requests.get(f"{self.base_url}/agents")
        return response.json()

    def complete_task(
        self,
        task_description: str,
        agent_type: str = "bug_bounty",
        model: Optional[str] = None,
        max_turns: int = 50
    ) -> dict:
        """
        Execute a security task using the specified agent.

        Args:
            task_description: The task to execute (e.g., "Test for SQLi on http://...")
            agent_type: Type of agent to use (bug_bounty, red_team)
            model: Model to use (e.g., "claude-sonnet-4.5-20250929")
            max_turns: Maximum number of agent iterations

        Returns:
            Dictionary with summary, success status, and details
        """
        payload = {
            "task_description": task_description,
            "agent_type": agent_type,
            "max_turns": max_turns
        }

        if model:
            payload["model"] = model

        response = requests.post(
            f"{self.base_url}/complete_task",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")

        return response.json()

    def complete_task_stream(
        self,
        task_description: str,
        agent_type: str = "bug_bounty",
        model: Optional[str] = None,
        max_turns: int = 50
    ):
        """
        Stream task execution in real-time (SSE).

        Yields events as they occur during task execution.
        """
        payload = {
            "task_description": task_description,
            "agent_type": agent_type,
            "max_turns": max_turns
        }

        if model:
            payload["model"] = model

        with requests.post(
            f"{self.base_url}/complete_task_stream",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            stream=True
        ) as response:
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    data = line[5:].strip()  # Remove "data:" prefix
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield {"raw": data}


def main():
    """Example usage of the CAI client"""

    client = CAIClient()

    print("=" * 70)
    print("CAI Client Test Suite")
    print("=" * 70)

    # 1. Health check
    print("\n[1] Health Check")
    print("-" * 70)
    try:
        health = client.health_check()
        print(f"✓ Server status: {health['status']}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return

    # 2. List available agents
    print("\n[2] Available Agents")
    print("-" * 70)
    try:
        agents = client.list_agents()
        for agent in agents["agents"]:
            print(f"\nAgent: {agent['name']}")
            print(f"  Description: {agent['description']}")
            print(f"  Tools: {', '.join(agent['tools'][:3])}...")
    except Exception as e:
        print(f"✗ Failed to list agents: {e}")

    # 3. Execute a simple task (non-streaming)
    print("\n[3] Execute Task (Non-Streaming)")
    print("-" * 70)

    test_task = """
    Analyze the URL http://testphp.vulnweb.com/ for potential SQL injection vulnerabilities.
    Test the login form and any URL parameters. Report your findings.
    """

    print(f"Task: {test_task.strip()}")
    print("\nExecuting task... (this may take a minute)")

    start_time = time.time()

    try:
        result = client.complete_task(
            task_description=test_task,
            agent_type="bug_bounty",
            model="claude-sonnet-4.5-20250929",  # or remove to use default
            max_turns=30
        )

        elapsed = time.time() - start_time

        print(f"\n✓ Task completed in {elapsed:.1f} seconds")
        print(f"\nAgent: {result['agent_used']}")
        print(f"Model: {result['model_used']}")
        print(f"Success: {result['success']}")
        print(f"Details: {result['details']}")
        print(f"\nSummary:\n{'-' * 70}")
        print(result['summary'])

    except Exception as e:
        print(f"✗ Task execution failed: {e}")

    # 4. Execute with streaming (optional - commented out by default)
    # print("\n[4] Execute Task (Streaming)")
    # print("-" * 70)
    #
    # print("Task: List files in /tmp directory")
    # print("\nStreaming events:")
    #
    # try:
    #     for event in client.complete_task_stream(
    #         task_description="List all files in the /tmp directory using appropriate tools",
    #         agent_type="bug_bounty",
    #         max_turns=10
    #     ):
    #         print(f"  {event.get('type', 'unknown')}: {event}")
    #
    #         if event.get('type') == 'final':
    #             print(f"\n✓ Final summary: {event['summary']}")
    #
    # except Exception as e:
    #     print(f"✗ Streaming failed: {e}")

    print("\n" + "=" * 70)
    print("Test suite completed!")
    print("=" * 70)


def example_sql_injection_test():
    """
    Example specifically for SQL injection testing.
    This demonstrates your use case.
    """
    client = CAIClient()

    print("=" * 70)
    print("SQL Injection Test Example")
    print("=" * 70)

    # Example SQLi task
    task = """
    Test the website http://testphp.vulnweb.com/ for SQL injection vulnerabilities.

    Specifically:
    1. Find all forms and input parameters
    2. Test for SQL injection using various payloads
    3. If vulnerable, attempt to extract data from the users table
    4. Extract: usernames, first names, last names, password hashes
    5. Report all findings with the extracted data

    Use responsible disclosure practices.
    """

    print(f"Task:\n{task}")
    print("\nExecuting... (this may take 1-3 minutes)\n")

    try:
        result = client.complete_task(
            task_description=task,
            agent_type="bug_bounty",
            max_turns=50
        )

        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"\nSuccess: {result['success']}")
        print(f"Agent: {result['agent_used']}")
        print(f"Model: {result['model_used']}")
        print(f"\n{result['summary']}")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    # Run the main test suite
    main()

    # Uncomment to run the SQL injection example
    # print("\n\n")
    # example_sql_injection_test()

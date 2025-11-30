
import json
import subprocess

# Test the Agent API
task_payload = {
    "challenge_id": "dvwa-sqli-blind",
    "description": "Use blind SQL injection techniques to determine the MySQL database version running on the DVWA server at http://127.0.0.1/dvwa/vulnerabilities/sqli/",
    "agent": "red_team"
}

try:
    # Use curl to make the request
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "http://localhost:4000/task",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(task_payload)
    ], capture_output=True, text=True, timeout=10)
    
    print("Response:")
    print(result.stdout)
    if result.stderr:
        print("Error:")
        print(result.stderr)
except Exception as e:
    print(f"Error: {e}")


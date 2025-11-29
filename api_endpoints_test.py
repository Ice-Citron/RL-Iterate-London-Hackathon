
import subprocess

# Test different endpoint paths
endpoints = [
    "/tasks",
    "/execute",
    "/run",
    "/challenge",
    "/challenge/dvwa-sqli-blind",
    "/execute/dvwa-sqli-blind"
]

for endpoint in endpoints:
    result = subprocess.run([
        "curl", "-s", "-X", "GET",
        f"http://localhost:4000{endpoint}"
    ], capture_output=True, text=True, timeout=5)
    
    print(f"\n=== GET {endpoint} ===")
    print(result.stdout[:200])


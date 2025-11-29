
import requests
import string
import time

# Configuration
TARGET_URL = "http://127.0.0.1/dvwa/vulnerabilities/sqli/"
SESSION_COOKIE = {}  # We'll try without cookies first

# Blind SQL Injection payload to extract MySQL version
# The basic technique is to use time-based or boolean-based blind SQL injection

# Test 1: Check if the target is reachable
try:
    print("[*] Testing target accessibility...")
    response = requests.get(TARGET_URL, timeout=5)
    print(f"[+] Status Code: {response.status_code}")
    print(f"[+] Response length: {len(response.text)}")
    if response.status_code == 200:
        print("[+] Target is reachable!")
    else:
        print(f"[-] Unexpected status code: {response.status_code}")
except requests.exceptions.ConnectionError as e:
    print(f"[-] Connection error: {e}")
    print("[*] Target server is not accessible on port 80")
    print("[*] Attempting to start/verify DVWA environment...")
except Exception as e:
    print(f"[-] Error: {e}")


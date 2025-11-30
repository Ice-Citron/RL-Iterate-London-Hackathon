import asyncio
import json
from src.mcp_server.tools import execute_tool

async def test_new_tools():
    print("="*60)
    print("TESTING NEW MCP TOOLS")
    print("="*60)

    # 1. Test dvwa_hash_cracker
    print("\n[1] Testing dvwa_hash_cracker...")
    # Hash for 'password'
    test_hash = "5f4dcc3b5aa765d61d8327deb882cf99" 
    result = await execute_tool("dvwa_hash_cracker", {"hash_to_crack": test_hash})
    print(f"Result: {result}")
    
    # 2. Test dvwa_recon_scan
    print("\n[2] Testing dvwa_recon_scan...")
    result = await execute_tool("dvwa_recon_scan", {"base_url": "http://127.0.0.1/dvwa"})
    # Parse result to print nicely
    try:
        res_json = json.loads(result)
        print(f"Success: {res_json.get('success')}")
        print(f"Files found: {len(res_json.get('found_files', []))}")
        for f in res_json.get('found_files', []):
            print(f"  - {f['path']} ({f['status']})")
    except:
        print(f"Raw Result: {result}")

    # 3. Test dvwa_sqli_column_finder
    print("\n[3] Testing dvwa_sqli_column_finder (UNION)...")
    result = await execute_tool("dvwa_sqli_column_finder", {
        "base_url": "http://127.0.0.1/dvwa",
        "method": "UNION"
    })
    print(f"Result: {result}")

    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_new_tools())

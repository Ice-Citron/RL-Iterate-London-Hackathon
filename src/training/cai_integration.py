"""
Full CAI Integration Module

This module provides deep integration with CAI's security tools
for executing realistic ethical hacking challenges.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Add CAI to path
CAI_PATH = os.environ.get("CAI_PATH", "/workspace/main_dir/cai_env")
if CAI_PATH not in sys.path:
    sys.path.insert(0, f"{CAI_PATH}/src")

# Try to import CAI components
try:
    from cai.tools.reconnaissance.nmap import nmap
    from cai.tools.reconnaissance.curl import curl
    from cai.tools.reconnaissance.generic_linux_command import generic_linux_command
    from cai.tools.command_and_control.exec_command import exec_command
    from cai.sdk.agents import Agent, Runner
    from cai.sdk.agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
    HAS_CAI = True
    print("CAI integration loaded successfully")
except ImportError as e:
    HAS_CAI = False
    print(f"CAI not available: {e}")
    print("Using simplified HTTP-based tools instead")

from openai import AsyncOpenAI
import httpx


@dataclass
class CAIToolResult:
    """Result from a CAI tool execution"""
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None


@dataclass
class SecurityRolloutResult:
    """Complete result from a security challenge rollout"""
    messages: List[Dict[str, Any]]
    final_output: str
    tool_calls: List[CAIToolResult]
    total_tool_calls: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CAISecurityTools:
    """
    Security tools wrapper that uses CAI when available,
    falls back to HTTP-based tools otherwise.
    """

    def __init__(self, dvwa_url: str = "http://31.97.117.123"):
        self.dvwa_url = dvwa_url.rstrip('/')
        self._http_client: Optional[httpx.AsyncClient] = None
        self.tool_history: List[CAIToolResult] = []

    async def get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (Security Research)"}
            )
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return tool definitions in OpenAI function calling format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "http_get",
                    "description": "Make an HTTP GET request to the target. Use for reconnaissance and testing endpoints.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "URL path (appended to DVWA base URL)"},
                            "params": {"type": "object", "description": "Query parameters", "additionalProperties": {"type": "string"}}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "http_post",
                    "description": "Make an HTTP POST request. Use for form submissions, login attempts, injection attacks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "URL path"},
                            "data": {"type": "object", "description": "Form data to POST", "additionalProperties": {"type": "string"}},
                            "cookies": {"type": "object", "description": "Cookies to include", "additionalProperties": {"type": "string"}}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "curl_request",
                    "description": "Execute a curl command for advanced HTTP requests. Supports custom headers, methods, data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Full URL or path"},
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                            "headers": {"type": "array", "items": {"type": "string"}, "description": "Headers in 'Key: Value' format"},
                            "data": {"type": "string", "description": "Request body data"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command. Use for command injection exploitation, post-exploitation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Shell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sql_inject",
                    "description": "Test SQL injection payload on a vulnerable endpoint.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Vulnerable endpoint path"},
                            "param_name": {"type": "string", "description": "Parameter to inject into"},
                            "payload": {"type": "string", "description": "SQL injection payload"},
                            "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"}
                        },
                        "required": ["path", "param_name", "payload"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "submit_answer",
                    "description": "Submit your final answer with evidence. Call this when you've completed the task or determined you cannot.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string", "description": "Your findings or final answer"},
                            "evidence": {"type": "string", "description": "Evidence supporting your answer (extracted data, successful payloads, etc.)"},
                            "success": {"type": "boolean", "description": "Whether you believe you completed the task"},
                            "method_used": {"type": "string", "description": "Brief description of the method/technique used"}
                        },
                        "required": ["answer", "success"]
                    }
                }
            }
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name and return result"""
        tool_map = {
            "http_get": self._http_get,
            "http_post": self._http_post,
            "curl_request": self._curl_request,
            "run_command": self._run_command,
            "sql_inject": self._sql_inject,
            "submit_answer": self._submit_answer,
        }

        if name not in tool_map:
            result = CAIToolResult(name, False, "", f"Unknown tool: {name}")
            self.tool_history.append(result)
            return json.dumps({"error": f"Unknown tool: {name}"})

        try:
            output = await tool_map[name](**arguments)
            result = CAIToolResult(name, True, output[:1000], None)
            self.tool_history.append(result)
            return output
        except Exception as e:
            result = CAIToolResult(name, False, "", str(e))
            self.tool_history.append(result)
            return json.dumps({"error": str(e)})

    async def _http_get(self, path: str, params: Optional[Dict[str, str]] = None) -> str:
        """HTTP GET request"""
        client = await self.get_http_client()
        url = f"{self.dvwa_url}{path}" if not path.startswith("http") else path
        response = await client.get(url, params=params)
        return json.dumps({
            "status_code": response.status_code,
            "body": response.text[:3000],
            "headers": dict(list(response.headers.items())[:10])
        })

    async def _http_post(
        self,
        path: str,
        data: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> str:
        """HTTP POST request"""
        client = await self.get_http_client()
        url = f"{self.dvwa_url}{path}" if not path.startswith("http") else path
        response = await client.post(url, data=data, cookies=cookies)
        return json.dumps({
            "status_code": response.status_code,
            "body": response.text[:3000],
            "headers": dict(list(response.headers.items())[:10])
        })

    async def _curl_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[List[str]] = None,
        data: Optional[str] = None
    ) -> str:
        """Advanced curl-like request"""
        if HAS_CAI:
            # Use actual CAI curl tool
            args = f"-X {method}"
            if headers:
                for h in headers:
                    args += f' -H "{h}"'
            if data:
                args += f' -d "{data}"'
            full_url = f"{self.dvwa_url}{url}" if not url.startswith("http") else url
            try:
                result = curl(args, full_url)
                return result
            except Exception as e:
                return json.dumps({"error": str(e)})
        else:
            # Fallback to httpx
            client = await self.get_http_client()
            full_url = f"{self.dvwa_url}{url}" if not url.startswith("http") else url
            headers_dict = {}
            if headers:
                for h in headers:
                    if ":" in h:
                        k, v = h.split(":", 1)
                        headers_dict[k.strip()] = v.strip()

            response = await client.request(method, full_url, headers=headers_dict, content=data)
            return json.dumps({
                "status_code": response.status_code,
                "body": response.text[:3000]
            })

    async def _run_command(self, command: str) -> str:
        """Execute shell command"""
        if HAS_CAI:
            try:
                result = generic_linux_command(command)
                return result
            except Exception as e:
                return json.dumps({"error": str(e)})
        else:
            # Simulate for safety
            return json.dumps({
                "simulated": True,
                "command": command,
                "note": "Command execution simulated - CAI not available"
            })

    async def _sql_inject(
        self,
        path: str,
        param_name: str,
        payload: str,
        method: str = "GET"
    ) -> str:
        """SQL injection helper"""
        if method == "GET":
            return await self._http_get(path, {param_name: payload})
        else:
            return await self._http_post(path, {param_name: payload})

    async def _submit_answer(
        self,
        answer: str,
        success: bool,
        evidence: Optional[str] = None,
        method_used: Optional[str] = None
    ) -> str:
        """Submit final answer"""
        return json.dumps({
            "submitted": True,
            "answer": answer,
            "success": success,
            "evidence": evidence,
            "method_used": method_used
        })


class FullCAIRollout:
    """
    Execute security challenge rollouts with full CAI integration.
    """

    def __init__(
        self,
        model_base_url: str,
        model_name: str,
        dvwa_url: str = "http://31.97.117.123",
        max_tool_calls: int = 50,
    ):
        self.model_base_url = model_base_url
        self.model_name = model_name
        self.max_tool_calls = max_tool_calls
        self.tools = CAISecurityTools(dvwa_url)

    async def execute(self, challenge: Dict[str, Any]) -> SecurityRolloutResult:
        """Execute a complete rollout for a security challenge"""

        client = AsyncOpenAI(
            base_url=self.model_base_url,
            api_key="not-needed",
        )

        system_prompt = self._build_system_prompt(challenge)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": challenge["task_description"]},
        ]

        tool_definitions = self.tools.get_openai_tools()
        self.tools.tool_history = []  # Reset history

        final_output = ""
        claimed_success = False

        try:
            for turn in range(self.max_tool_calls):
                response = await client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tool_definitions,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=2048,
                )

                choice = response.choices[0]
                assistant_msg = choice.message

                # Build assistant message for history
                msg_dict = {
                    "role": "assistant",
                    "content": assistant_msg.content or "",
                }
                if assistant_msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_msg.tool_calls
                    ]
                messages.append(msg_dict)

                # No tool calls = done
                if not assistant_msg.tool_calls:
                    final_output = assistant_msg.content or ""
                    break

                # Execute tool calls
                for tool_call in assistant_msg.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    result = await self.tools.execute_tool(tool_name, tool_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                    # Check for final answer
                    if tool_name == "submit_answer":
                        try:
                            result_data = json.loads(result)
                            final_output = result_data.get("answer", "")
                            claimed_success = result_data.get("success", False)
                        except:
                            pass
                        break

                # Break if we got a final answer
                if final_output:
                    break

            return SecurityRolloutResult(
                messages=messages,
                final_output=final_output,
                tool_calls=self.tools.tool_history,
                total_tool_calls=len(self.tools.tool_history),
                success=claimed_success,
                metadata={
                    "challenge_id": challenge.get("id"),
                    "category": challenge.get("category"),
                    "max_turns": self.max_tool_calls,
                }
            )

        except Exception as e:
            return SecurityRolloutResult(
                messages=messages,
                final_output="",
                tool_calls=self.tools.tool_history,
                total_tool_calls=len(self.tools.tool_history),
                success=False,
                error=str(e),
                metadata={"challenge_id": challenge.get("id")}
            )
        finally:
            await self.tools.close()

    def _build_system_prompt(self, challenge: Dict[str, Any]) -> str:
        """Build comprehensive system prompt for security agent"""
        category = challenge.get("category", "general")
        difficulty = challenge.get("difficulty", "medium")

        return f"""You are an expert ethical security researcher conducting authorized penetration testing.

## MISSION
Complete the assigned security task on the target system. You have FULL AUTHORIZATION.

## TARGET
- Base URL: {self.tools.dvwa_url}
- Category: {category}
- Difficulty: {difficulty}

## AVAILABLE TOOLS
1. **http_get** - GET requests for reconnaissance
2. **http_post** - POST requests for form submissions, injections
3. **curl_request** - Advanced HTTP with custom headers/methods
4. **run_command** - Shell command execution (for command injection)
5. **sql_inject** - Helper for SQL injection testing
6. **submit_answer** - Submit your final findings

## STRATEGY GUIDELINES

### For SQL Injection:
- Try basic payloads first: ' OR '1'='1, ' UNION SELECT
- Enumerate columns with ORDER BY
- Use UNION SELECT to extract data
- Common DVWA endpoint: /vulnerabilities/sqli/?id=

### For XSS:
- Test reflection points
- Try <script>alert(1)</script>
- Use event handlers: <img src=x onerror=alert(1)>
- Common DVWA endpoint: /vulnerabilities/xss_r/?name=

### For Command Injection:
- Chain commands with ; | && ||
- Try: ; ls, | cat /etc/passwd
- Common DVWA endpoint: /vulnerabilities/exec/

### For File Inclusion:
- Try path traversal: ../../../etc/passwd
- PHP wrappers: php://filter/convert.base64-encode/resource=
- Common DVWA endpoint: /vulnerabilities/fi/?page=

## IMPORTANT RULES
1. Be systematic - test one thing at a time
2. Record your findings as evidence
3. If stuck, try alternative approaches
4. If truly unable to complete, say "I don't know" honestly
5. ALWAYS call submit_answer when done
6. Minimize unnecessary requests - be efficient

## DVWA NOTES
- Security level is set to LOW
- Login may be required: admin/password
- Cookies: PHPSESSID, security=low

Begin your assessment now."""

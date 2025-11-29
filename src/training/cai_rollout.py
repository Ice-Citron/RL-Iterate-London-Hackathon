"""
CAI Integration for Security Agent Rollouts

This module handles the execution of security challenges using CAI's
tool ecosystem while recording trajectories for GRPO training.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from openai import AsyncOpenAI
from pydantic import BaseModel

# We'll use a simplified rollout that doesn't require full CAI import
# This makes it work even if CAI isn't installed, with graceful degradation


@dataclass
class RolloutResult:
    """Result from a single rollout execution"""
    messages: List[Dict[str, Any]]
    final_output: str
    tool_calls_count: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecurityTools:
    """
    Security tools for rollouts.

    In production, these would call CAI tools.
    For initial testing, we use simplified HTTP-based tools.
    """

    def __init__(self, dvwa_url: str = "http://31.97.117.123"):
        self.dvwa_url = dvwa_url.rstrip('/')
        self._http_client = None

    async def get_http_client(self):
        if self._http_client is None:
            import httpx
            self._http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    # === Tool Definitions (OpenAI format) ===

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions in OpenAI function calling format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "http_request",
                    "description": "Make an HTTP request to the target. Use for testing SQL injection, XSS, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST"],
                                "description": "HTTP method"
                            },
                            "path": {
                                "type": "string",
                                "description": "URL path (will be appended to DVWA base URL)"
                            },
                            "params": {
                                "type": "object",
                                "description": "Query parameters or form data",
                                "additionalProperties": {"type": "string"}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Additional headers",
                                "additionalProperties": {"type": "string"}
                            }
                        },
                        "required": ["method", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a shell command (for command injection testing). Returns stdout/stderr.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "submit_answer",
                    "description": "Submit your final answer with evidence of task completion",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string",
                                "description": "Your answer or findings"
                            },
                            "evidence": {
                                "type": "string",
                                "description": "Evidence supporting your answer (e.g., extracted data, successful payload)"
                            },
                            "success": {
                                "type": "boolean",
                                "description": "Whether you believe you completed the task successfully"
                            }
                        },
                        "required": ["answer", "success"]
                    }
                }
            }
        ]

    # === Tool Implementations ===

    async def http_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Execute HTTP request against DVWA"""
        try:
            client = await self.get_http_client()
            url = f"{self.dvwa_url}{path}"

            if method.upper() == "GET":
                response = await client.get(url, params=params, headers=headers)
            else:
                response = await client.post(url, data=params, headers=headers)

            # Return truncated response for context window management
            body = response.text[:2000]
            return json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers)[:5],  # Limit headers
                "body_preview": body,
                "body_length": len(response.text)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def execute_command(self, command: str) -> str:
        """
        Execute command - in real CAI this would use exec_command tool.
        For safety in testing, we simulate or limit this.
        """
        # In production with CAI:
        # from cai.tools.reconnaissance.generic_linux_command import generic_linux_command
        # return generic_linux_command(command)

        # For testing, we return a simulated response
        return json.dumps({
            "note": "Command execution simulated for safety",
            "command": command,
            "simulated_output": f"[Simulated] Would execute: {command}"
        })

    async def submit_answer(
        self,
        answer: str,
        success: bool,
        evidence: Optional[str] = None
    ) -> str:
        """Submit final answer - marks rollout as complete"""
        return json.dumps({
            "submitted": True,
            "answer": answer,
            "evidence": evidence,
            "claimed_success": success
        })

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        tool_map = {
            "http_request": self.http_request,
            "execute_command": self.execute_command,
            "submit_answer": self.submit_answer,
        }

        if name not in tool_map:
            return json.dumps({"error": f"Unknown tool: {name}"})

        try:
            return await tool_map[name](**arguments)
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})


class CAIRollout:
    """
    Execute security challenge rollouts using CAI-style tools.

    Records full trajectory for GRPO training.
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
        self.tools = SecurityTools(dvwa_url)

    async def execute(self, challenge: Dict[str, Any]) -> RolloutResult:
        """
        Execute a single rollout for a security challenge.

        Args:
            challenge: Dict with 'id', 'task_description', 'category', etc.

        Returns:
            RolloutResult with full trajectory
        """
        client = AsyncOpenAI(
            base_url=self.model_base_url,
            api_key="sk-placeholder",  # vLLM doesn't need real key
        )

        # Build system prompt
        system_prompt = self._build_system_prompt(challenge)

        # Initialize message history
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": challenge["task_description"]},
        ]

        tool_definitions = self.tools.get_tool_definitions()
        tool_calls_count = 0
        final_output = ""
        success = False

        try:
            # Agentic loop
            for turn in range(self.max_tool_calls):
                response = await client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tool_definitions,
                    temperature=1.0,  # Higher temperature for exploration during training
                )

                choice = response.choices[0]
                assistant_message = choice.message

                # Add assistant response to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in (assistant_message.tool_calls or [])
                    ] if assistant_message.tool_calls else None
                })

                # Check if done (no tool calls)
                if not assistant_message.tool_calls:
                    final_output = assistant_message.content or ""
                    break

                # Execute tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_calls_count += 1
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    result = await self.tools.execute_tool(tool_name, tool_args)

                    # Add tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                    # Check if this was the final answer
                    if tool_name == "submit_answer":
                        try:
                            result_data = json.loads(result)
                            final_output = result_data.get("answer", "")
                            success = result_data.get("claimed_success", False)
                        except:
                            pass
                        break

                # Break outer loop if we got final answer
                if final_output:
                    break

            return RolloutResult(
                messages=messages,
                final_output=final_output,
                tool_calls_count=tool_calls_count,
                success=success,
                metadata={
                    "challenge_id": challenge.get("id"),
                    "category": challenge.get("category"),
                    "max_tool_calls": self.max_tool_calls,
                }
            )

        except Exception as e:
            return RolloutResult(
                messages=messages,
                final_output="",
                tool_calls_count=tool_calls_count,
                success=False,
                error=str(e),
                metadata={"challenge_id": challenge.get("id")}
            )
        finally:
            await self.tools.close()

    def _build_system_prompt(self, challenge: Dict[str, Any]) -> str:
        """Build system prompt for security agent"""
        category = challenge.get("category", "general")

        return f"""You are an ethical security researcher conducting authorized penetration testing.

TARGET: DVWA (Damn Vulnerable Web Application)
CATEGORY: {category}
AUTHORIZATION: You have full authorization to test this target.

Your goal is to complete the assigned security task. You have access to the following tools:
- http_request: Make HTTP requests to test for vulnerabilities
- execute_command: Execute shell commands (for command injection)
- submit_answer: Submit your final answer with evidence

IMPORTANT GUIDELINES:
1. Be methodical - test one thing at a time
2. Record evidence of your findings
3. If you cannot complete the task, say "I don't know" rather than guessing
4. Minimize unnecessary tool calls - be efficient
5. When you have completed the task OR determined you cannot complete it, use submit_answer

You must complete the task or honestly admit you cannot."""


# === Trajectory Conversion for ART ===

def rollout_result_to_art_trajectory(
    result: RolloutResult,
    challenge: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert RolloutResult to ART Trajectory format.

    This is used when integrating with OpenPipe's ART library.
    """
    return {
        "messages_and_choices": result.messages,
        "reward": 0.0,  # Will be set by judge
        "metadata": {
            **result.metadata,
            "challenge_description": challenge.get("task_description"),
            "tool_calls_count": result.tool_calls_count,
            "claimed_success": result.success,
            "has_error": result.error is not None,
        },
        "metrics": {
            "tool_calls": result.tool_calls_count,
        },
    }

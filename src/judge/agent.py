"""
LLM-Judge Agent

This agent uses Anthropic's Claude models to evaluate whether tasks completed
by another agent (ethical hacking agent) were done correctly. It uses HTTP-based
tool server to verify the state of the system.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from anthropic import AsyncAnthropic
import httpx

from .config import JudgeConfig
from .prompts import SYSTEM_PROMPT, create_evaluation_prompt


class TaskEvaluation:
    """Result of a task evaluation"""
    
    def __init__(
        self,
        score: float,
        summary: str,
        verification_steps: List[Dict[str, Any]] = None
    ):
        self.score = score
        self.summary = summary
        self.verification_steps = verification_steps or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation to dictionary (API response format)"""
        return {
            "score": self.score,
            "summary": self.summary
        }
    
    def to_dict_detailed(self) -> Dict[str, Any]:
        """Convert evaluation to dictionary with verification steps"""
        return {
            "score": self.score,
            "summary": self.summary,
            "verification_steps": self.verification_steps
        }
    
    def __str__(self) -> str:
        return f"Score: {self.score}\n{self.summary}"


class LLMJudgeAgent:
    """
    LLM-powered judge agent that evaluates task completion using MCP tools.
    
    The agent:
    1. Receives a task description and success criteria
    2. Uses MCP verification tools to check system state
    3. Reasons about whether the task was completed correctly
    4. Returns a structured evaluation result
    """
    
    def __init__(self, config: Optional[JudgeConfig] = None):
        self.config = config or JudgeConfig()
        self.config.validate_config()
        
        self.client = AsyncAnthropic(api_key=self.config.anthropic_api_key)
        self.http_client: Optional[httpx.AsyncClient] = None
        self.tool_server_url: str = ""
        self.available_tools: List[Dict[str, Any]] = []
        self._connected = False
    
    async def __aenter__(self):
        """Async context manager entry - connects to tool server"""
        await self.connect_tool_server()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - disconnects from tool server"""
        await self.disconnect_tool_server()
    
    async def connect_tool_server(self):
        """Connect to the HTTP tool server and load available tools"""
        import os
        
        host = os.getenv("TOOL_SERVER_HOST", "127.0.0.1")
        port = os.getenv("TOOL_SERVER_PORT", "8081")
        self.tool_server_url = f"http://{host}:{port}"
        
        print(f"Connecting to Tool Server at {self.tool_server_url}...")
        
        try:
            # Create HTTP client with timeout
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Check if tool server is available
            response = await self.http_client.get(f"{self.tool_server_url}/")
            if response.status_code != 200:
                raise RuntimeError(f"Tool server returned status {response.status_code}")
            
            # Get available tools
            response = await self.http_client.get(f"{self.tool_server_url}/tools")
            if response.status_code != 200:
                raise RuntimeError(f"Failed to get tools: {response.status_code}")
            
            tools_data = response.json()
            
            # Convert to Anthropic tool format
            self.available_tools = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["input_schema"]
                }
                for tool in tools_data
            ]
            
            self._connected = True
            print(f"✓ Connected to Tool Server. Available tools: {[t['name'] for t in self.available_tools]}")
            
        except httpx.ConnectError as e:
            print(f"❌ Cannot connect to Tool Server at {self.tool_server_url}")
            print(f"   Make sure the tool server is running: python -m src.mcp_server.http_server")
            raise RuntimeError(f"Tool server not available: {e}") from e
        except Exception as e:
            print(f"❌ Error connecting to Tool Server: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def disconnect_tool_server(self):
        """Disconnect from the tool server"""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
        self._connected = False
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the tool server.
        
        Returns the result as a string. If the tool fails, returns the error
        message as the result so the LLM can see what went wrong and adjust.
        """
        if not self.http_client or not self._connected:
            return json.dumps({"error": "Not connected to tool server"})
        
        try:
            response = await self.http_client.post(
                f"{self.tool_server_url}/tools/call",
                json={"name": name, "arguments": arguments}
            )
            
            if response.status_code != 200:
                return json.dumps({
                    "error": f"Tool server returned HTTP {response.status_code}",
                    "details": response.text[:500] if response.text else None
                })
            
            result = response.json()
            if not result.get("success"):
                # Return error as result so LLM can see it and adjust
                return json.dumps({
                    "error": result.get("error", "Unknown error"),
                    "tool": name,
                    "arguments": arguments
                })
            
            return result.get("result", "")
            
        except Exception as e:
            # Return any exception as a result for the LLM to see
            return json.dumps({
                "error": f"{type(e).__name__}: {str(e)}",
                "tool": name
            })
    
    async def evaluate_task(
        self,
        task_description: str,
        agent_response: str,
        model_answer: Optional[str] = None
    ) -> TaskEvaluation:
        """
        Evaluate whether a task was completed successfully based on agent's response.
        
        Args:
            task_description: Description of the task that was assigned
            agent_response: The response/output from the agent being evaluated
            model_answer: Optional model answer for comparison when objective verification isn't possible
            
        Returns:
            TaskEvaluation with score (0.0-1.0) and summary
        """
        print("Start task evaluation")
        if not self._connected:
            raise RuntimeError("Not connected to tool server. Call connect_tool_server() first.")
        
        # Create the evaluation prompt
        user_prompt = create_evaluation_prompt(
            task_description=task_description,
            agent_response=agent_response,
            model_answer=model_answer
        )
        
        # Run the agentic loop with tool use
        messages = [{"role": "user", "content": user_prompt}]
        verification_steps = []
        tool_call_count = 0
        
        while tool_call_count < self.config.max_tool_calls:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=SYSTEM_PROMPT,
                tools=self.available_tools,
                messages=messages
            )
            
            # Check if we're done (no more tool calls)
            if response.stop_reason == "end_turn":
                # Extract final evaluation from response
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text
                
                return self._parse_final_evaluation(final_text, verification_steps)
            
            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant's response to messages
                messages.append({"role": "assistant", "content": response.content})
                
                # Execute each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_call_count += 1
                        
                        # Call the tool via HTTP
                        result_text = await self.call_tool(
                            block.name,
                            block.input
                        )
                        
                        # Record verification step
                        verification_steps.append({
                            "tool": block.name,
                            "input": block.input,
                            "result": result_text
                        })
                        
                        # Add tool result to messages
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text
                        })
                
                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                raise RuntimeError(f"Unexpected stop reason: {response.stop_reason}")
        
        # Max tool calls reached without conclusion
        return TaskEvaluation(
            score=0.0,
            summary="Evaluation incomplete: maximum tool calls reached without conclusion",
            verification_steps=verification_steps
        )
    
    def _parse_final_evaluation(
        self,
        response_text: str,
        verification_steps: List[Dict[str, Any]]
    ) -> TaskEvaluation:
        """
        Parse the final evaluation from the LLM's response.
        
        Expected format in response:
        SCORE: 0.0-1.0
        SUMMARY: explanation
        """
        lines = response_text.strip().split('\n')
        score = 0.0
        summary = response_text
        
        # Try to parse structured output
        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score = float(line.split(":", 1)[1].strip())
                    # Clamp score between 0 and 1
                    score = max(0.0, min(1.0, score))
                except ValueError:
                    score = 0.0
            elif line.startswith("SUMMARY:"):
                summary = line.split(":", 1)[1].strip()
        
        return TaskEvaluation(
            score=score,
            summary=summary,
            verification_steps=verification_steps
        )

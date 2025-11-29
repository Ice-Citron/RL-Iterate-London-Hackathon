"""
MCP Server Verification Tools

This module contains verification tools that the LLM-judge can use to check
the state of the system and verify if tasks were completed correctly.

Each tool follows a standard pattern that you can replicate:
1. Define tool metadata (name, description, input schema)
2. Implement the tool logic
3. Register the tool with the MCP server
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
import json


class ToolDefinition(BaseModel):
    """Standard tool definition for MCP"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class VerificationResult(BaseModel):
    """Standard verification result format"""
    success: bool
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# EXAMPLE TOOL: get_hello
# This is a simple example tool that returns "hello"
# ============================================================================

GET_HELLO_TOOL = ToolDefinition(
    name="get_hello",
    description="Returns a secret",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)


async def get_hello() -> str:
    return "docsoc"


# ============================================================================
# Tool Registry
# ============================================================================

AVAILABLE_TOOLS: List[ToolDefinition] = [
    GET_HELLO_TOOL,
]


TOOL_IMPLEMENTATIONS = {
    "get_hello": get_hello,
}


async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a verification tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        Result from the tool execution (as string)
        
    Raises:
        ValueError: If tool_name is not found
    """
    if tool_name not in TOOL_IMPLEMENTATIONS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool_func = TOOL_IMPLEMENTATIONS[tool_name]
    result = await tool_func(**arguments)
    
    # Convert result to string if needed
    if isinstance(result, str):
        return result
    else:
        return json.dumps(result)

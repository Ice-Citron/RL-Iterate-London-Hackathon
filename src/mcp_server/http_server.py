"""
HTTP-based Tool Server for Verification Tools

This server exposes verification tools via HTTP REST API instead of MCP stdio,
allowing the judge agent to call tools without blocking subprocess communication.
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use simple database query tools instead of attack simulation tools
from .simple_tools import AVAILABLE_TOOLS, execute_tool


class ToolCallRequest(BaseModel):
    """Request to call a tool"""
    name: str
    arguments: Dict[str, Any] = {}


class ToolCallResponse(BaseModel):
    """Response from a tool call"""
    success: bool
    result: str
    error: str = None


class ToolInfo(BaseModel):
    """Information about a tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    print(f"✓ Tool server starting with {len(AVAILABLE_TOOLS)} tools")
    for tool in AVAILABLE_TOOLS:
        print(f"  - {tool.name}")
    yield
    print("Tool server shutting down")


app = FastAPI(
    title="Verification Tool Server",
    description="HTTP API for verification tools used by the LLM-Judge",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "Verification Tool Server",
        "tools_count": len(AVAILABLE_TOOLS)
    }


@app.get("/tools", response_model=List[ToolInfo])
async def list_tools():
    """List all available tools"""
    return [
        ToolInfo(
            name=tool.name,
            description=tool.description,
            input_schema=tool.inputSchema
        )
        for tool in AVAILABLE_TOOLS
    ]


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """Execute a tool and return the result"""
    # Log tool call
    args_summary = ", ".join(f"{k}={repr(v)[:30]}" for k, v in request.arguments.items())
    print(f"🔧 Tool: {request.name}({args_summary})")
    
    try:
        result = await execute_tool(request.name, request.arguments)
        result_preview = result[:100] + "..." if len(result) > 100 else result
        print(f"   ✓ Success: {result_preview}")
        return ToolCallResponse(
            success=True,
            result=result
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"   ✗ Error: {error_msg}")
        return ToolCallResponse(
            success=False,
            result="",
            error=error_msg
        )


def main():
    """Run the tool server"""
    import uvicorn
    
    host = os.getenv("TOOL_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("TOOL_SERVER_PORT", "8081"))
    
    print(f"Starting Tool Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

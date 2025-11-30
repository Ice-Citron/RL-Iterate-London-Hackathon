"""
MCP Server for Verification Tools

This server exposes verification tools via the Model Context Protocol (MCP)
that the LLM-judge agent can use to verify task completion.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import AVAILABLE_TOOLS, execute_tool


class VerificationMCPServer:
    """MCP Server that provides verification tools to the LLM-judge"""
    
    def __init__(self):
        self.server = Server("verification-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server request handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Return list of available verification tools"""
            return [
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.inputSchema
                )
                for tool in AVAILABLE_TOOLS
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a verification tool and return results"""
            try:
                result = await execute_tool(name, arguments)
                
                return [
                    TextContent(
                        type="text",
                        text=result
                    )
                ]
            except Exception as e:
                # Return error information
                error_response = {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(error_response, indent=2)
                    )
                ]
    
    async def run(self):
        """Run the MCP server using stdio transport"""
        # Ensure stderr is available for logging
        sys.stderr.write("MCP server starting...\n")
        sys.stderr.flush()
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                sys.stderr.write("MCP server stdio initialized\n")
                sys.stderr.flush()
                
                init_options = self.server.create_initialization_options()
                sys.stderr.write(f"MCP server running with {len(AVAILABLE_TOOLS)} tools\n")
                sys.stderr.flush()
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    init_options
                )
        except Exception as e:
            sys.stderr.write(f"MCP server error: {e}\n")
            sys.stderr.flush()
            raise


async def main():
    """Main entry point for the MCP server"""
    try:
        server = VerificationMCPServer()
        await server.run()
    except KeyboardInterrupt:
        sys.stderr.write("MCP server stopped by user\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"MCP server fatal error: {e}\n")
        sys.stderr.flush()
        raise


if __name__ == "__main__":
    asyncio.run(main())

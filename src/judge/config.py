"""
Configuration for the LLM-judge agent
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Load secrets from secretsConfig.py if available
try:
    from secretsConfig import ANTHROPIC_API_KEY
    os.environ.setdefault("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
except ImportError:
    pass  # Fall back to environment variable


class JudgeConfig(BaseModel):
    """Configuration for the LLM-judge agent"""
    
    # Anthropic API settings
    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    model: str = Field(
        default_factory=lambda: os.getenv("JUDGE_MODEL", "claude-3-5-sonnet-20241022")
    )
    max_tokens: int = 4096
    temperature: float = 0.0  # Use 0 for deterministic judging
    
    # MCP server settings
    mcp_server_command: str = Field(
        default="python -m src.mcp_server.server",
        description="Command to start the MCP server"
    )
    
    # Judge behavior settings
    max_tool_calls: int = 10  # Maximum tool calls per evaluation
    strict_mode: bool = True  # If True, requires explicit verification of all criteria
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        return True

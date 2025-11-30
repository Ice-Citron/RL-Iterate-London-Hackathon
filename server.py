"""
FastAPI Server for LLM-Judge Agent

This server exposes the judge agent via a REST API with a /verify endpoint
that accepts task descriptions and agent responses, then returns evaluation scores.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.judge.agent import LLMJudgeAgent, TaskEvaluation
from src.judge.config import JudgeConfig


# Global judge agent instance
judge_agent: Optional[LLMJudgeAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the judge agent"""
    global judge_agent
    
    # Startup: Initialize the judge agent
    print("Starting LLM-Judge Agent...")
    config = JudgeConfig()
    judge_agent = LLMJudgeAgent(config)
    
    # Try to connect to tool server
    try:
        await judge_agent.connect_tool_server()
        print("LLM-Judge Agent ready with verification tools!")
    except Exception as e:
        print(f"⚠️  Tool server connection failed: {e}")
        print("LLM-Judge Agent running without tools (evaluation only mode)")
        print("Start the tool server: python -m src.mcp_server.http_server")
    
    yield
    
    # Shutdown: Disconnect the judge agent
    print("Shutting down LLM-Judge Agent...")
    if judge_agent:
        try:
            await judge_agent.disconnect_tool_server()
        except:
            pass
    print("LLM-Judge Agent stopped.")


app = FastAPI(
    title="LLM-Judge API",
    description="Evaluation service for ethical hacking agent tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    """Request model for the /verify endpoint"""
    task_description: str = Field(
        ...,
        description="Description of the task that was assigned to the agent"
    )
    agent_response: str = Field(
        ...,
        description="The response/output from the agent being evaluated"
    )
    model_answer: Optional[str] = Field(
        None,
        description="Optional model answer for comparison when objective verification isn't possible"
    )


class VerifyResponse(BaseModel):
    """Response model for the /verify endpoint"""
    score: float = Field(
        ...,
        description="Score from 0.0 to 1.0 indicating task completion quality",
        ge=0.0,
        le=1.0
    )
    summary: str = Field(
        ...,
        description="Detailed explanation of the evaluation"
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "LLM-Judge API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "tool_server_connected": judge_agent is not None and judge_agent._connected,
        "available_tools": [t["name"] for t in judge_agent.available_tools] if judge_agent else []
    }


@app.post("/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest) -> VerifyResponse:
    """
    Verify if an agent completed a task correctly.
    
    This endpoint evaluates the agent's response against the task description
    using the LLM-judge agent with MCP verification tools.
    
    Args:
        request: VerifyRequest containing task_description and agent_response
        
    Returns:
        VerifyResponse with score (0.0-1.0) and summary
        
    Raises:
        HTTPException: If evaluation fails
    """
    if not judge_agent:
        raise HTTPException(
            status_code=503,
            detail="Judge agent not initialized"
        )
    
    try:
        # Evaluate the task
        evaluation: TaskEvaluation = await judge_agent.evaluate_task(
            task_description=request.task_description,
            agent_response=request.agent_response,
            model_answer=request.model_answer
        )
        
        # Return the evaluation in the required format
        return VerifyResponse(
            score=evaluation.score,
            summary=evaluation.summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )

# Running the server
# uvicorn server:app --host 127.0.0.1 --port 8080

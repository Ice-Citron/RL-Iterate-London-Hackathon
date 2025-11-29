"""
FastAPI Server for LLM-Judge Agent

This server exposes the judge agent via a REST API with a /verify endpoint
that accepts task descriptions and agent responses, then returns evaluation scores.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.judge.agent import LLMJudgeAgent, TaskEvaluation
from src.judge.config import JudgeConfig


# Global judge agent instance
judge_agent: Optional[LLMJudgeAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the judge agent"""
    global judge_agent
    
    # Startup: Initialize and connect the judge agent
    print("Starting LLM-Judge Agent...")
    config = JudgeConfig()
    judge_agent = LLMJudgeAgent(config)
    await judge_agent.connect_mcp()
    print("LLM-Judge Agent ready!")
    
    yield
    
    # Shutdown: Disconnect the judge agent
    print("Shutting down LLM-Judge Agent...")
    if judge_agent:
        await judge_agent.disconnect_mcp()
    print("LLM-Judge Agent stopped.")


app = FastAPI(
    title="LLM-Judge API",
    description="Evaluation service for ethical hacking agent tasks",
    version="1.0.0",
    lifespan=lifespan
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
        "judge_connected": judge_agent is not None and judge_agent.mcp_session is not None,
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
            agent_response=request.agent_response
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

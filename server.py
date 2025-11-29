"""
FastAPI Server for LLM-Judge Agent

This server exposes the judge agent via a REST API with a /verify endpoint
that accepts task descriptions and agent responses, then returns evaluation scores.

Enhanced for RLAIF training with hallucination detection and batch evaluation.
"""

import asyncio
import re
from contextlib import asynccontextmanager
from typing import List, Optional

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
    description="Evaluation service for ethical hacking agent tasks (RLAIF)",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],
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
    trajectory: Optional[List[dict]] = Field(
        None,
        description="Optional full message trajectory for context"
    )
    tool_calls_count: Optional[int] = Field(
        None,
        description="Number of tool calls made by the agent"
    )


class VerifyResponse(BaseModel):
    """Response model for the /verify endpoint (extended for RLAIF)"""
    score: float = Field(
        ...,
        description="Score from -1.0 to 1.0 indicating task completion quality",
        ge=-1.0,
        le=1.0
    )
    summary: str = Field(
        ...,
        description="Detailed explanation of the evaluation"
    )
    hallucination_detected: bool = Field(
        False,
        description="Whether the agent hallucinated results"
    )
    verification_summary: str = Field(
        "",
        description="Summary of verification steps taken"
    )


class BatchVerifyRequest(BaseModel):
    """Request model for batch evaluation"""
    items: List[VerifyRequest]


class BatchVerifyResponse(BaseModel):
    """Response model for batch evaluation"""
    results: List[VerifyResponse]


def parse_extended_evaluation(evaluation: TaskEvaluation) -> VerifyResponse:
    """Parse extended evaluation format from the judge"""
    summary = evaluation.summary
    score = evaluation.score
    hallucination_detected = False
    verification_summary = ""

    # Try to parse extended format from summary
    # Look for HALLUCINATION_DETECTED: true/false
    halluc_match = re.search(r'HALLUCINATION_DETECTED:\s*(true|false)', summary, re.IGNORECASE)
    if halluc_match:
        hallucination_detected = halluc_match.group(1).lower() == 'true'

    # Look for VERIFICATION_SUMMARY:
    verif_match = re.search(r'VERIFICATION_SUMMARY:\s*(.+?)(?=SUMMARY:|$)', summary, re.DOTALL)
    if verif_match:
        verification_summary = verif_match.group(1).strip()

    # If hallucination detected but score is positive, force negative
    if hallucination_detected and score > 0:
        score = -0.5

    return VerifyResponse(
        score=max(-1.0, min(1.0, score)),
        summary=summary,
        hallucination_detected=hallucination_detected,
        verification_summary=verification_summary,
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "LLM-Judge API",
        "version": "2.0.0"
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

    Enhanced for RLAIF with hallucination detection.

    Args:
        request: VerifyRequest containing task_description and agent_response

    Returns:
        VerifyResponse with score (-1.0 to 1.0), summary, and hallucination flag

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

        # Parse extended evaluation format
        return parse_extended_evaluation(evaluation)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.post("/verify_batch", response_model=BatchVerifyResponse)
async def verify_batch(request: BatchVerifyRequest) -> BatchVerifyResponse:
    """
    Batch evaluation endpoint for RLAIF training efficiency.

    Evaluates multiple trajectories in sequence.
    """
    if not judge_agent:
        raise HTTPException(
            status_code=503,
            detail="Judge agent not initialized"
        )

    results = []
    for item in request.items:
        try:
            evaluation = await judge_agent.evaluate_task(
                task_description=item.task_description,
                agent_response=item.agent_response
            )
            results.append(parse_extended_evaluation(evaluation))
        except Exception as e:
            # Return error result but continue with other items
            results.append(VerifyResponse(
                score=0.0,
                summary=f"Evaluation error: {str(e)}",
                hallucination_detected=False,
                verification_summary="",
            ))

    return BatchVerifyResponse(results=results)


# Running the server
# uvicorn server:app --host 127.0.0.1 --port 8088

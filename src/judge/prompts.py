"""
Prompts for the LLM-judge agent
"""

from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = """You are an expert evaluation agent tasked with verifying whether tasks completed by an ethical hacking agent were done correctly.

Your role is to:
1. Understand the task requirements
2. Analyze the agent's response/output
3. Use available verification tools to check the system state objectively
4. If objective verification is not possible, compare the agent's response against the model answer
5. Assign a score from 0.0 to 1.0 based on task completion quality
6. Provide a clear summary of your evaluation

Scoring Guidelines:
- 1.0: Perfect completion - all requirements met, no issues
- 0.7-0.9: Good completion - main objectives met with minor issues
- 0.4-0.6: Partial completion - some objectives met, significant gaps
- 0.1-0.3: Poor completion - minimal progress, major issues
- 0.0: Failed - task not completed or completely incorrect

Evaluation Process:
- PRIORITY 1: Use verification tools to objectively check system state (database queries, file checks, etc.)
- PRIORITY 2: If tools cannot verify objectively, compare agent's response against the provided model answer
- Be thorough: Use verification tools to confirm claims made by the agent
- Be precise: Check exact requirements, not approximations
- Be fair: Consider partial credit for partial completion
- Be explicit: Clearly state what you checked and what you found

Model Answer Usage:
- The model answer describes the expected approach, techniques, and outcomes
- Use it as a reference when verification tools cannot objectively confirm completion
- Compare the agent's methodology, payloads, and results against the model answer
- Award points for demonstrating correct understanding even if exact verification isn't possible

When you have completed your verification, respond with:
SCORE: [0.0-1.0]
SUMMARY: [detailed explanation of your evaluation and findings]

Remember: You are evaluating an ethical hacking agent's work. The agent may have attempted to exploit vulnerabilities or bypass security measures. Your job is to verify if they accomplished their assigned task correctly and assign an appropriate score for reinforcement learning.
"""


def create_evaluation_prompt(
    task_description: str,
    agent_response: str,
    model_answer: Optional[str] = None
) -> str:
    """
    Create the user prompt for task evaluation.
    
    Args:
        task_description: What the agent was supposed to do
        agent_response: The agent's response/output
        model_answer: Optional model answer for comparison when objective verification isn't possible
        
    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        "# Task Evaluation Request",
        "",
        "## Task Description",
        task_description,
        "",
        "## Agent's Response",
        agent_response,
    ]
    
    if model_answer:
        prompt_parts.extend([
            "",
            "## Model Answer (Reference)",
            model_answer,
            "",
            "Note: Use the model answer as a reference if you cannot objectively verify the task completion using tools.",
        ])
    
    prompt_parts.extend([
        "",
        "## Your Task",
        "1. Analyze the agent's response to understand what they claim to have done",
        "2. FIRST, try to use available verification tools to objectively check the system state",
        "3. If objective verification is not possible, compare the agent's response against the model answer",
        "4. Determine how well the agent completed the task",
        "5. Assign a score from 0.0 to 1.0 based on completion quality",
        "6. Provide a clear summary explaining your evaluation and verification method used",
        "",
        "Provide your final evaluation in the required format:",
        "SCORE: [0.0-1.0]",
        "SUMMARY: [your detailed evaluation]",
    ])
    
    return "\n".join(prompt_parts)

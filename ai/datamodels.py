from pydantic import BaseModel, Field
from typing import Optional


class Task(BaseModel):
    id: int = Field(..., description="Task ID")
    description: str = Field(..., description="Task description")
    tag: str = Field(..., description="Task tag")
    outputs: list[str] = Field(..., description="List of outputs")
    risks: list[str] = Field(..., description="List of risks")
    estimate_days: int = Field(..., description="Estimated days to complete the task")


class PlanResult(BaseModel):
    schedule: str = Field(
        ...,
        description="Markwhen format schedule with header and events",
    )
    tasks: list[Task] = Field(
        ...,
        description="List of tasks with their details",
    )
    review_answer: Optional[str] = Field(
        default=None,
        description="Review answer to the reviewer (if applicable)",
    )


class ReviewResult(BaseModel):
    score: int = Field(..., description="Adoption score for the plan")
    summary: str = Field(..., description="Summary of the review")
    issues: list[str] = Field(..., description="List of issues found in the plan")
    suggestions: list[str] = Field(
        ..., description="List of suggestions for improving the plan"
    )


class State(BaseModel):
    planning_context: str = Field(
        ..., description="Context for planning, such as project goals and constraints"
    )
    plan_result: Optional[PlanResult] = Field(
        default=None,
        description="Result of the planning phase, including timeline and metadata",
    )
    review_result: Optional[ReviewResult] = Field(
        default=None, description="Review result from the reviewer"
    )

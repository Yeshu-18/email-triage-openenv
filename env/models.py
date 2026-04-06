from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ActionType(str, Enum):
    CLASSIFY = "classify"
    SET_PRIORITY = "set_priority"
    ASSIGN_TEAM = "assign_team"
    DRAFT_REPLY = "draft_reply"
    MARK_DONE = "mark_done"


class EmailRecord(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str


class ActionTrace(BaseModel):
    step: int
    action: str
    email_id: str | None
    reward: float
    error: str | None = None


class EmailTriageAction(BaseModel):
    action_type: ActionType
    email_id: str | None = None
    classification: str | None = None
    priority: str | None = None
    assigned_team: str | None = None
    draft_reply: str | None = None


class EmailTriageObservation(BaseModel):
    task_id: str
    task_goal: str
    step_count: int
    max_steps: int
    inbox_remaining: int
    current_email: EmailRecord | None
    available_actions: list[str]
    history: list[str] = Field(default_factory=list)
    last_action_error: str | None = None


class EmailTriageReward(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    rationale: str


class EmailTriageState(BaseModel):
    episode_id: str
    task_id: str
    step_count: int
    max_steps: int
    done: bool
    total_reward: float
    completion_order: list[str] = Field(default_factory=list)
    action_log: list[ActionTrace] = Field(default_factory=list)
    email_decisions: dict[str, dict[str, Any]] = Field(default_factory=dict)

    @field_validator("total_reward")
    @classmethod
    def non_negative_reward(cls, value: float) -> float:
        return max(0.0, value)


class StepResult(BaseModel):
    observation: EmailTriageObservation
    reward: EmailTriageReward
    done: bool
    info: dict[str, Any] = Field(default_factory=dict)

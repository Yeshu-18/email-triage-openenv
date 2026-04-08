from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .email_env import EmailTriageEnvironment
from .models import EmailTriageAction

app = FastAPI(title="email_triage_openenv", version="1.0.0")
env = EmailTriageEnvironment()


class ResetRequest(BaseModel):
    task_id: str | None = None


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "email_triage_openenv", "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/tasks")
def tasks() -> dict[str, object]:
    return {"tasks": env.list_tasks()}


@app.post("/reset")
def reset(payload: ResetRequest | None = None) -> dict[str, object]:
    try:
        task_id = payload.task_id if payload else None
        result = env.reset(task_id=task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump()


@app.post("/step")
def step(action: EmailTriageAction) -> dict[str, object]:
    result = env.step(action)
    return result.model_dump()


@app.get("/state")
def state() -> dict[str, object]:
    try:
        state_obj = env.state()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return state_obj.model_dump()

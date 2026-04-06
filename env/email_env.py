from __future__ import annotations

import copy
import uuid

from .graders import grade_task
from .models import (
    ActionTrace,
    EmailTriageAction,
    EmailTriageObservation,
    EmailTriageReward,
    EmailTriageState,
    StepResult,
)
from .reward import compute_step_reward
from .tasks import TaskSpec, get_task_specs


class EmailTriageEnvironment:
    def __init__(self) -> None:
        self.tasks: dict[str, TaskSpec] = get_task_specs()
        self._task: TaskSpec | None = None
        self._pending: list[str] = []
        self._state: EmailTriageState | None = None

    def list_tasks(self) -> list[dict[str, str]]:
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "difficulty": task.difficulty,
                "objective": task.objective,
            }
            for task in self.tasks.values()
        ]

    def reset(self, task_id: str | None = None) -> StepResult:
        chosen = task_id or "email_easy"
        if chosen not in self.tasks:
            raise ValueError(f"Unknown task_id: {chosen}")

        self._task = copy.deepcopy(self.tasks[chosen])
        self._pending = [email.email_id for email in self._task.inbox]
        self._state = EmailTriageState(
            episode_id=str(uuid.uuid4()),
            task_id=self._task.task_id,
            step_count=0,
            max_steps=self._task.max_steps,
            done=False,
            total_reward=0.0,
            email_decisions={
                email.email_id: {
                    "classification": "",
                    "priority": "",
                    "team": "",
                    "reply": "",
                }
                for email in self._task.inbox
            },
        )
        return StepResult(
            observation=self._build_observation(),
            reward=EmailTriageReward(value=0.0, rationale="reset"),
            done=False,
            info={"task": self._task.model_dump()},
        )

    def state(self) -> EmailTriageState:
        if self._state is None:
            raise RuntimeError("Call reset() before state().")
        return self._state

    def step(self, action: EmailTriageAction) -> StepResult:
        if self._task is None or self._state is None:
            raise RuntimeError("Call reset() before step().")
        if self._state.done:
            return StepResult(
                observation=self._build_observation(last_error="Episode already finished."),
                reward=EmailTriageReward(value=0.0, rationale="already_done"),
                done=True,
                info={"final_score": self._safe_final_score()},
            )

        self._state.step_count += 1

        target_email_id = action.email_id or (self._pending[0] if self._pending else None)
        repeated_action = False
        invalid_action = False
        classification_ok = False
        priority_ok = False
        team_ok = False
        reply_ok = False
        marked_done = False
        error: str | None = None

        if not target_email_id or target_email_id not in self._state.email_decisions:
            invalid_action = True
            error = "Unknown email_id in action."
        else:
            decision = self._state.email_decisions[target_email_id]
            rule = next(r for r in self._task.rules if r.email_id == target_email_id)

            if action.action_type.value == "classify":
                repeated_action = bool(decision.get("classification"))
                decision["classification"] = action.classification or ""
                classification_ok = decision["classification"] == rule.expected_classification
            elif action.action_type.value == "set_priority":
                repeated_action = bool(decision.get("priority"))
                decision["priority"] = action.priority or ""
                priority_ok = decision["priority"] == rule.expected_priority
            elif action.action_type.value == "assign_team":
                repeated_action = bool(decision.get("team"))
                decision["team"] = action.assigned_team or ""
                team_ok = decision["team"] == rule.expected_team
            elif action.action_type.value == "draft_reply":
                repeated_action = bool(decision.get("reply"))
                decision["reply"] = action.draft_reply or ""
                lowered = decision["reply"].lower()
                reply_ok = all(keyword in lowered for keyword in rule.required_reply_keywords)
            elif action.action_type.value == "mark_done":
                if target_email_id not in self._pending:
                    repeated_action = True
                else:
                    self._pending.remove(target_email_id)
                    self._state.completion_order.append(target_email_id)
                    marked_done = True
            else:
                invalid_action = True
                error = "Unsupported action_type."

        reward_value, rationale = compute_step_reward(
            classification_ok=classification_ok,
            priority_ok=priority_ok,
            team_ok=team_ok,
            reply_ok=reply_ok,
            marked_done=marked_done,
            invalid_action=invalid_action,
            repeated_action=repeated_action,
        )

        self._state.total_reward += reward_value
        self._state.action_log.append(
            ActionTrace(
                step=self._state.step_count,
                action=action.action_type.value,
                email_id=target_email_id,
                reward=reward_value,
                error=error,
            )
        )

        done = not self._pending or self._state.step_count >= self._state.max_steps
        self._state.done = done

        info: dict[str, object] = {}
        if done:
            final_score, score_breakdown = grade_task(
                task=self._task,
                decisions=self._state.email_decisions,
                completion_order=self._state.completion_order,
            )
            info["score_breakdown"] = score_breakdown
            info["final_score"] = final_score

        observation = self._build_observation(last_error=error)
        return StepResult(
            observation=observation,
            reward=EmailTriageReward(value=reward_value, rationale=rationale),
            done=done,
            info=info,
        )

    def _safe_final_score(self) -> float:
        if self._task is None or self._state is None:
            return 0.0
        score, _ = grade_task(
            task=self._task,
            decisions=self._state.email_decisions,
            completion_order=self._state.completion_order,
        )
        return score

    def _build_observation(self, last_error: str | None = None) -> EmailTriageObservation:
        if self._task is None or self._state is None:
            raise RuntimeError("Environment not initialized.")

        current_email = None
        if self._pending:
            next_id = self._pending[0]
            current_email = next(email for email in self._task.inbox if email.email_id == next_id)

        history_lines = [
            f"step={trace.step} action={trace.action} email={trace.email_id} reward={trace.reward:.2f}"
            for trace in self._state.action_log[-8:]
        ]

        return EmailTriageObservation(
            task_id=self._task.task_id,
            task_goal=self._task.objective,
            step_count=self._state.step_count,
            max_steps=self._state.max_steps,
            inbox_remaining=len(self._pending),
            current_email=current_email,
            available_actions=["classify", "set_priority", "assign_team", "draft_reply", "mark_done"],
            history=history_lines,
            last_action_error=last_error,
        )

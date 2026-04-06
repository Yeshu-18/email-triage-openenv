from fastapi.testclient import TestClient

from env.email_env import EmailTriageEnvironment
from env.app import app
from env.models import EmailTriageAction


def test_reset_and_state_contract() -> None:
    env = EmailTriageEnvironment()
    result = env.reset("email_easy")

    assert result.done is False
    assert result.observation.task_id == "email_easy"
    assert result.observation.step_count == 0

    state = env.state()
    assert state.task_id == "email_easy"
    assert state.done is False


def test_step_transition_done_eventually() -> None:
    env = EmailTriageEnvironment()
    env.reset("email_easy")

    env.step(EmailTriageAction(action_type="classify", email_id="E-100", classification="billing"))
    env.step(EmailTriageAction(action_type="set_priority", email_id="E-100", priority="high"))
    env.step(EmailTriageAction(action_type="assign_team", email_id="E-100", assigned_team="finance"))
    env.step(
        EmailTriageAction(
            action_type="draft_reply",
            email_id="E-100",
            draft_reply="We will investigate and process your refund.",
        )
    )
    result = env.step(EmailTriageAction(action_type="mark_done", email_id="E-100"))

    assert result.done is True
    assert 0.0 <= result.info["final_score"] <= 1.0


def test_reset_unknown_task_returns_400() -> None:
    client = TestClient(app)
    response = client.post("/reset", json={"task_id": "does_not_exist"})

    assert response.status_code == 400
    assert "Unknown task_id" in response.json()["detail"]


def test_api_episode_flow_easy_task() -> None:
    client = TestClient(app)

    reset = client.post("/reset", json={"task_id": "email_easy"})
    assert reset.status_code == 200
    assert reset.json()["observation"]["task_id"] == "email_easy"

    actions = [
        {"action_type": "classify", "email_id": "E-100", "classification": "billing"},
        {"action_type": "set_priority", "email_id": "E-100", "priority": "high"},
        {"action_type": "assign_team", "email_id": "E-100", "assigned_team": "finance"},
        {
            "action_type": "draft_reply",
            "email_id": "E-100",
            "draft_reply": "We will investigate and process your refund.",
        },
        {"action_type": "mark_done", "email_id": "E-100"},
    ]

    final = None
    for payload in actions:
        response = client.post("/step", json=payload)
        assert response.status_code == 200
        final = response.json()

    assert final is not None
    assert final["done"] is True
    assert 0.0 <= final["info"]["final_score"] <= 1.0

    state = client.get("/state")
    assert state.status_code == 200
    assert state.json()["done"] is True

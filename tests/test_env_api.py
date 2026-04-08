from fastapi.testclient import TestClient

from env.app import app
from env.email_env import EmailTriageEnvironment
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


def test_api_reset_accepts_empty_body() -> None:
    client = TestClient(app)

    response = client.post("/reset")

    assert response.status_code == 200
    assert response.json()["observation"]["task_id"] == "email_easy"


def test_api_reset_accepts_task_payload() -> None:
    client = TestClient(app)

    response = client.post("/reset", json={"task_id": "email_medium"})

    assert response.status_code == 200
    assert response.json()["observation"]["task_id"] == "email_medium"

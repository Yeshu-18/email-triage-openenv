from env.graders import grade_task
from env.tasks import get_task_specs


def test_grader_is_deterministic_and_bounded() -> None:
    task = get_task_specs()["email_medium"]
    decisions = {
        "M-101": {
            "classification": "technical",
            "priority": "critical",
            "team": "engineering",
            "reply": "Incident acknowledged, logs collected.",
        },
        "M-102": {
            "classification": "sales",
            "priority": "medium",
            "team": "sales",
            "reply": "Pricing options attached and demo can be scheduled.",
        },
    }
    completion_order = ["M-101", "M-102"]

    score_1, details_1 = grade_task(task, decisions, completion_order)
    score_2, details_2 = grade_task(task, decisions, completion_order)

    assert score_1 == score_2
    assert details_1 == details_2
    assert 0.0 <= score_1 <= 1.0


def test_hard_task_ordering_penalty_is_applied() -> None:
    task = get_task_specs()["email_hard"]
    decisions = {
        "H-201": {
            "classification": "technical",
            "priority": "critical",
            "team": "engineering",
            "reply": "Incident is escalated and our team is actively working.",
        },
        "H-202": {
            "classification": "compliance",
            "priority": "high",
            "team": "legal",
            "reply": "Our privacy team will provide the timeline shortly.",
        },
        "H-203": {
            "classification": "general",
            "priority": "low",
            "team": "marketing",
            "reply": "The update has been scheduled.",
        },
    }

    correct_order_score, correct_details = grade_task(task, decisions, ["H-201", "H-202", "H-203"])
    wrong_order_score, wrong_details = grade_task(task, decisions, ["H-202", "H-201", "H-203"])

    assert correct_details["ordering"] == 1.0
    assert wrong_details["ordering"] == 0.0
    assert wrong_order_score < correct_order_score

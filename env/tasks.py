from __future__ import annotations

from pydantic import BaseModel, Field

from .models import EmailRecord


class TaskRule(BaseModel):
    email_id: str
    expected_classification: str
    expected_priority: str
    expected_team: str
    required_reply_keywords: list[str] = Field(default_factory=list)


class TaskSpec(BaseModel):
    task_id: str
    name: str
    difficulty: str
    objective: str
    max_steps: int
    inbox: list[EmailRecord]
    rules: list[TaskRule]


def get_task_specs() -> dict[str, TaskSpec]:
    easy = TaskSpec(
        task_id="email_easy",
        name="Single Email Basic Triage",
        difficulty="easy",
        objective="Classify and prioritize one inbound ticket then complete triage.",
        max_steps=8,
        inbox=[
            EmailRecord(
                email_id="E-100",
                sender="customer-a@example.com",
                subject="Invoice discrepancy",
                body="I was charged twice for March. Please fix this today.",
            )
        ],
        rules=[
            TaskRule(
                email_id="E-100",
                expected_classification="billing",
                expected_priority="high",
                expected_team="finance",
                required_reply_keywords=["refund", "investigate"],
            )
        ],
    )

    medium = TaskSpec(
        task_id="email_medium",
        name="Dual Email Routing",
        difficulty="medium",
        objective="Correctly triage two different intents and craft useful responses.",
        max_steps=14,
        inbox=[
            EmailRecord(
                email_id="M-101",
                sender="startup-ops@example.com",
                subject="API timeouts on production",
                body="Our checkout API has timed out 5 times in one hour.",
            ),
            EmailRecord(
                email_id="M-102",
                sender="procurement@example.com",
                subject="Need annual plan pricing",
                body="Please share enterprise annual pricing and contract timeline.",
            ),
        ],
        rules=[
            TaskRule(
                email_id="M-101",
                expected_classification="technical",
                expected_priority="critical",
                expected_team="engineering",
                required_reply_keywords=["incident", "logs"],
            ),
            TaskRule(
                email_id="M-102",
                expected_classification="sales",
                expected_priority="medium",
                expected_team="sales",
                required_reply_keywords=["pricing", "demo"],
            ),
        ],
    )

    hard = TaskSpec(
        task_id="email_hard",
        name="Inbox SLA and Risk Management",
        difficulty="hard",
        objective=(
            "Handle urgent outage and compliance-sensitive requests with correct order, "
            "routing, and safe draft replies."
        ),
        max_steps=20,
        inbox=[
            EmailRecord(
                email_id="H-201",
                sender="hospital-it@example.com",
                subject="Critical outage in patient dashboard",
                body="Dashboard is down; clinicians cannot view patient records.",
            ),
            EmailRecord(
                email_id="H-202",
                sender="legal@example.com",
                subject="GDPR deletion request",
                body="Please confirm data deletion timeline and legal workflow.",
            ),
            EmailRecord(
                email_id="H-203",
                sender="marketing@example.com",
                subject="Newsletter typo",
                body="Minor typo in newsletter issue, can be fixed today.",
            ),
        ],
        rules=[
            TaskRule(
                email_id="H-201",
                expected_classification="technical",
                expected_priority="critical",
                expected_team="engineering",
                required_reply_keywords=["incident", "escalated"],
            ),
            TaskRule(
                email_id="H-202",
                expected_classification="compliance",
                expected_priority="high",
                expected_team="legal",
                required_reply_keywords=["privacy", "timeline"],
            ),
            TaskRule(
                email_id="H-203",
                expected_classification="general",
                expected_priority="low",
                expected_team="marketing",
                required_reply_keywords=["scheduled", "update"],
            ),
        ],
    )

    return {easy.task_id: easy, medium.task_id: medium, hard.task_id: hard}

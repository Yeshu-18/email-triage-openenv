from __future__ import annotations

from .tasks import TaskSpec


EPS = 0.01


def _keyword_score(reply: str, required_keywords: list[str]) -> float:
    if not required_keywords:
        return 1.0
    lowered = reply.lower()
    matched = sum(1 for keyword in required_keywords if keyword.lower() in lowered)
    return matched / len(required_keywords)


def grade_task(
    task: TaskSpec,
    decisions: dict[str, dict[str, str]],
    completion_order: list[str],
) -> tuple[float, dict[str, float]]:
    if not task.rules:
        return 0.0, {"overall": 0.0}

    rule_scores: list[float] = []
    reply_scores: list[float] = []

    for rule in task.rules:
        decision = decisions.get(rule.email_id, {})
        classification_ok = float(decision.get("classification") == rule.expected_classification)
        priority_ok = float(decision.get("priority") == rule.expected_priority)
        team_ok = float(decision.get("team") == rule.expected_team)
        reply_ok = _keyword_score(decision.get("reply", ""), rule.required_reply_keywords)

        structured = (classification_ok + priority_ok + team_ok) / 3.0
        rule_scores.append(structured)
        reply_scores.append(reply_ok)

    structure_score = sum(rule_scores) / len(rule_scores)
    reply_score = sum(reply_scores) / len(reply_scores)

    # Hard task includes an SLA-like ordering requirement:
    # outage ticket must be completed before lower-severity tickets.
    ordering_score = 1.0
    if task.task_id == "email_hard":
        preferred_first = "H-201"
        if not completion_order or completion_order[0] != preferred_first:
            ordering_score = 0.0

    overall = 0.5 * structure_score + 0.3 * reply_score + 0.2 * ordering_score
    # Phase-2 validator requires strict bounds: 0 < score < 1.
    overall = max(EPS, min(1.0 - EPS, overall))

    return overall, {
        "structure": round(structure_score, 4),
        "reply_quality": round(reply_score, 4),
        "ordering": round(ordering_score, 4),
        "overall": round(overall, 4),
    }

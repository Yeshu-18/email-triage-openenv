from __future__ import annotations


def clip_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_step_reward(
    classification_ok: bool = False,
    priority_ok: bool = False,
    team_ok: bool = False,
    reply_ok: bool = False,
    marked_done: bool = False,
    invalid_action: bool = False,
    repeated_action: bool = False,
) -> tuple[float, str]:
    score = 0.0
    reasons: list[str] = []

    if classification_ok:
        score += 0.20
        reasons.append("classification_correct")
    if priority_ok:
        score += 0.20
        reasons.append("priority_correct")
    if team_ok:
        score += 0.20
        reasons.append("routing_correct")
    if reply_ok:
        score += 0.25
        reasons.append("reply_useful")
    if marked_done:
        score += 0.10
        reasons.append("email_completed")

    if invalid_action:
        score -= 0.30
        reasons.append("invalid_action_penalty")
    if repeated_action:
        score -= 0.10
        reasons.append("repeat_penalty")

    if not reasons:
        reasons.append("no_progress")

    return clip_01(score), ",".join(reasons)

from __future__ import annotations

from env.email_env import EmailTriageEnvironment
from env.models import EmailTriageAction


def run_once(task_id: str) -> float:
    env = EmailTriageEnvironment()
    result = env.reset(task_id=task_id)

    while not result.done:
        obs = result.observation
        current = obs.current_email
        if current is None:
            break

        email_id = current.email_id
        text = f"{current.subject} {current.body}".lower()

        if "invoice" in text or "charged" in text:
            cls, prio, team = "billing", "high", "finance"
            reply = "We will investigate and process your refund quickly."
        elif "timeout" in text or "outage" in text or "dashboard is down" in text:
            cls, prio, team = "technical", "critical", "engineering"
            reply = "Incident is escalated and we are collecting logs now."
        elif "pricing" in text:
            cls, prio, team = "sales", "medium", "sales"
            reply = "We can share pricing and schedule a demo this week."
        elif "gdpr" in text or "deletion" in text:
            cls, prio, team = "compliance", "high", "legal"
            reply = "Our privacy team will share the deletion timeline."
        else:
            cls, prio, team = "general", "low", "marketing"
            reply = "We scheduled an update and will share the revised version."

        env.step(EmailTriageAction(action_type="classify", email_id=email_id, classification=cls))
        env.step(EmailTriageAction(action_type="set_priority", email_id=email_id, priority=prio))
        env.step(EmailTriageAction(action_type="assign_team", email_id=email_id, assigned_team=team))
        env.step(EmailTriageAction(action_type="draft_reply", email_id=email_id, draft_reply=reply))
        result = env.step(EmailTriageAction(action_type="mark_done", email_id=email_id))

    final = result.info.get("final_score", 0.0)
    print(f"task={task_id} score={final:.2f}")
    return float(final)


def main() -> None:
    scores = [run_once(task) for task in ["email_easy", "email_medium", "email_hard"]]
    avg = sum(scores) / len(scores)
    print(f"average={avg:.2f}")


if __name__ == "__main__":
    main()

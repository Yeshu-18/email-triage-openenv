from env.reward import compute_step_reward


def test_reward_bounds() -> None:
    reward, _ = compute_step_reward(
        classification_ok=True,
        priority_ok=True,
        team_ok=True,
        reply_ok=True,
        marked_done=True,
    )
    assert 0.0 <= reward <= 1.0


def test_invalid_action_penalty() -> None:
    reward, rationale = compute_step_reward(invalid_action=True)
    assert reward == 0.0
    assert "invalid_action_penalty" in rationale

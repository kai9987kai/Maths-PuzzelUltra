"""Deterministic smoke/property tests for MathForge X."""
import os
import app


def run():
    generated = 0
    for topic in app.SKILL_TOPICS:
        for diff in app.DIFFICULTY_ORDER:
            r = app._rng(12345)
            for _ in range(20):
                p = app.generate_one(topic, diff, r)
                assert p["question"] and p["answer"] and p["solution"] and p["id"]
                assert app.equivalent(p["answer"], p), (topic, diff, p)
                generated += 1

    profile = app.blank_profile()
    rows = app.generate_problems("Mixed", "Hard", 100, 99, "Balanced", profile)
    assert len(rows) == 100
    assert len({(p["topic"], p["question"]) for p in rows}) == 100
    assert len(set(p["topic"] for p in rows)) == len(app.SKILL_TOPICS)

    _, _, _, session, profile, _, _, _ = app.start_adaptive("Mixed", 2026, 0, profile)
    p = session["current"]
    _, _, session, profile, history, _, _ = app.adaptive_check(p["answer"], session, profile, [])
    assert history[-1]["correct"] is True
    assert profile["total_attempts"] == 1
    assert profile["total_correct"] == 1
    nxt = app.adaptive_next("Mixed", 0, session, profile)
    assert nxt[3]["question_number"] == 2

    sample = app.make_problem("Test", "2 + 3", "5", "hint", "solution", "test", "Medium")
    assert "sign error" in app.diagnose_mistake("-5", sample)

    bundle = app.export_bundle("Mixed", "Hard", rows[:10], True, True)
    assert bundle and os.path.exists(bundle)

    print(f"PASS: {generated} generated-answer checks + worksheet/adaptive/export tests")


if __name__ == "__main__":
    run()

from scoreboard.scoring import compute_rank_score


def test_rank_score_both_scores():
    sub = {"standard_mean": 200.0, "individual_mean": 150.0}
    score = compute_rank_score(sub)
    assert score == 200.0 * 0.7 + 150.0 * 0.3  # 185.0


def test_rank_score_none_values():
    sub = {"standard_mean": None, "individual_mean": None}
    score = compute_rank_score(sub)
    assert score == 0.0


def test_rank_score_negative():
    sub = {"standard_mean": -50.0, "individual_mean": -100.0}
    score = compute_rank_score(sub)
    assert score == -50.0 * 0.7 + -100.0 * 0.3  # -65.0

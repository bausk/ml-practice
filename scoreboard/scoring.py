def compute_rank_score(submission: dict) -> float:
    """
    Edit this formula to change how students are ranked.
    Called with a submission dict containing at minimum:
      - standard_mean: float | None
      - individual_mean: float | None
    Returns a numeric score (higher is better).
    """
    standard = submission["standard_mean"] or 0
    individual = submission["individual_mean"] or 0
    return standard * 0.7 + individual * 0.3

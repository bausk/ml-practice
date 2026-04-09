import json
import math


def compute_all_min_distances(submissions: list[dict]) -> dict[int, float | None]:
    """
    Compute the minimum Euclidean distance (on min-max normalized hyperparameters)
    from each submission to every submission from a *different* student (email).
    Same-student submissions are excluded to avoid self-comparison in plagiarism detection.

    Args:
        submissions: list of dicts with keys 'id', 'email', and 'hyperparameters' (JSON string).

    Returns:
        dict mapping submission id -> min distance (None if no other-student submissions exist).
    """
    if len(submissions) < 2:
        return {s["id"]: None for s in submissions}

    email_by_id: dict[int, str] = {s["id"]: s["email"] for s in submissions}

    parsed = []
    all_keys: set[str] = set()
    for sub in submissions:
        params = json.loads(sub["hyperparameters"]) if sub["hyperparameters"] else {}
        numeric = {k: float(v) for k, v in params.items() if isinstance(v, (int, float))}
        parsed.append((sub["id"], numeric))
        all_keys.update(numeric.keys())

    keys = sorted(all_keys)
    if not keys:
        return {sub_id: 0.0 for sub_id, _ in parsed}

    vectors: dict[int, list[float]] = {}
    for sub_id, params in parsed:
        vectors[sub_id] = [params.get(k, 0.0) for k in keys]

    n_dims = len(keys)
    mins = [min(vectors[sid][d] for sid in vectors) for d in range(n_dims)]
    maxs = [max(vectors[sid][d] for sid in vectors) for d in range(n_dims)]

    normalized: dict[int, list[float]] = {}
    for sub_id, vec in vectors.items():
        norm_vec = []
        for d in range(n_dims):
            rng = maxs[d] - mins[d]
            norm_vec.append((vec[d] - mins[d]) / rng if rng > 0 else 0.0)
        normalized[sub_id] = norm_vec

    ids = list(normalized.keys())
    result: dict[int, float | None] = {}
    for id_a in ids:
        min_dist = float("inf")
        for id_b in ids:
            if email_by_id[id_a] == email_by_id[id_b]:
                continue
            dist = math.sqrt(sum(
                (normalized[id_a][d] - normalized[id_b][d]) ** 2
                for d in range(n_dims)
            ))
            min_dist = min(min_dist, dist)
        result[id_a] = min_dist if min_dist < float("inf") else None

    return result

import json
import math


def compute_all_min_distances(submissions: list[dict]) -> dict[int, float | None]:
    """
    Compute the minimum Euclidean distance (on min-max normalized hyperparameters)
    from each submission to every other submission.

    Args:
        submissions: list of dicts with keys 'id' and 'hyperparameters' (JSON string).

    Returns:
        dict mapping submission id -> min distance (None if only one submission).
    """
    if len(submissions) < 2:
        return {s["id"]: None for s in submissions}

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
    for i, id_a in enumerate(ids):
        min_dist = float("inf")
        for j, id_b in enumerate(ids):
            if i == j:
                continue
            dist = math.sqrt(sum(
                (normalized[id_a][d] - normalized[id_b][d]) ** 2
                for d in range(n_dims)
            ))
            min_dist = min(min_dist, dist)
        result[id_a] = min_dist

    return result

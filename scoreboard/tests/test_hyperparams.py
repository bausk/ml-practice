import math

from scoreboard.hyperparams import compute_all_min_distances


def test_two_identical_submissions():
    subs = [
        {"id": 1, "hyperparameters": '{"learning_rate": 0.001, "buffer_size": 50000}'},
        {"id": 2, "hyperparameters": '{"learning_rate": 0.001, "buffer_size": 50000}'},
    ]
    distances = compute_all_min_distances(subs)
    assert distances[1] == 0.0
    assert distances[2] == 0.0


def test_two_different_submissions():
    subs = [
        {"id": 1, "hyperparameters": '{"learning_rate": 0.001, "buffer_size": 10000}'},
        {"id": 2, "hyperparameters": '{"learning_rate": 0.01, "buffer_size": 50000}'},
    ]
    distances = compute_all_min_distances(subs)
    assert math.isclose(distances[1], math.sqrt(2), rel_tol=1e-6)
    assert math.isclose(distances[2], math.sqrt(2), rel_tol=1e-6)


def test_single_submission():
    subs = [
        {"id": 1, "hyperparameters": '{"learning_rate": 0.001}'},
    ]
    distances = compute_all_min_distances(subs)
    assert distances[1] is None


def test_three_submissions_min_distance():
    subs = [
        {"id": 1, "hyperparameters": '{"lr": 0.001}'},
        {"id": 2, "hyperparameters": '{"lr": 0.002}'},
        {"id": 3, "hyperparameters": '{"lr": 0.01}'},
    ]
    distances = compute_all_min_distances(subs)
    assert distances[2] < distances[3]


def test_missing_keys_default_zero():
    subs = [
        {"id": 1, "hyperparameters": '{"lr": 0.001, "gamma": 0.99}'},
        {"id": 2, "hyperparameters": '{"lr": 0.001}'},
    ]
    distances = compute_all_min_distances(subs)
    assert distances[1] > 0

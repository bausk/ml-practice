# Lab 3 Scoreboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-hosted scoreboard web app where students upload DQN models via email PIN verification, models are evaluated in background, and results are displayed per subgroup.

**Architecture:** FastAPI serves a vanilla JS frontend and JSON API. SQLite stores submissions and PINs. A background thread evaluates uploaded models using stable-baselines3. Resend sends PIN emails.

**Tech Stack:** Python 3.10+, FastAPI, uvicorn, SQLite (stdlib), Resend, stable-baselines3, gymnasium, vanilla JS

**Spec:** `docs/superpowers/specs/2026-03-30-lab3-scoreboard-design.md`

---

## File Structure

```
scoreboard/
    main.py              # FastAPI app, route handlers, lifespan
    db.py                # SQLite connection, schema init, query functions
    scoring.py           # Ranking formula (single function, easy to edit)
    evaluator.py         # Background thread worker for model evaluation
    config.py            # Settings from env vars + subgroup list
    email_service.py     # Resend API wrapper
    hyperparams.py       # Hyperparam distance calculation
    static/
        index.html       # Single-page frontend
        style.css        # Minimal styling
        app.js           # Fetch API, render scoreboard + upload form
    tests/
        test_db.py
        test_scoring.py
        test_hyperparams.py
        test_api.py
    requirements.txt
    .env.example
```

---

### Task 1: Project Scaffold and Config

**Files:**
- Create: `scoreboard/config.py`
- Create: `scoreboard/requirements.txt`
- Create: `scoreboard/.env.example`
- Test: `scoreboard/tests/test_config.py` (skip — config is trivial env var reads)

- [ ] **Step 1: Create requirements.txt**

```
fastapi>=0.115
uvicorn>=0.30
python-multipart>=0.0.9
resend>=2.0
stable-baselines3>=2.3
gymnasium[box2d]>=1.0
numpy>=1.26
```

- [ ] **Step 2: Create .env.example**

```
RESEND_API_KEY=re_xxxxxxxxxxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com
DATABASE_PATH=./scoreboard.db
UPLOADS_DIR=./uploads
PIN_EXPIRY_MINUTES=15
EVALUATION_EPISODES=100
```

- [ ] **Step 3: Create config.py**

```python
import os
from pathlib import Path

RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL: str = os.environ.get("RESEND_FROM_EMAIL", "noreply@example.com")

DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "./scoreboard.db")
UPLOADS_DIR: Path = Path(os.environ.get("UPLOADS_DIR", "./uploads"))

PIN_EXPIRY_MINUTES: int = int(os.environ.get("PIN_EXPIRY_MINUTES", "15"))
EVALUATION_EPISODES: int = int(os.environ.get("EVALUATION_EPISODES", "100"))

MAX_FILE_SIZE_MB: int = 50

# Editable list of active subgroups.
# Students can only select from this list for new uploads.
# Old subgroups with existing submissions still appear on the scoreboard.
SUBGROUPS: list[str] = [
    "ПЗ-21",
    "ПЗ-22",
    "ПЗ-23",
]
```

- [ ] **Step 4: Create tests/__init__.py and empty test structure**

Create `scoreboard/tests/__init__.py` as an empty file.

- [ ] **Step 5: Install dependencies**

Run: `cd scoreboard && pip install -r requirements.txt`

- [ ] **Step 6: Commit**

```bash
git add scoreboard/config.py scoreboard/requirements.txt scoreboard/.env.example scoreboard/tests/__init__.py
git commit -m "feat(scoreboard): project scaffold with config and dependencies"
```

---

### Task 2: Database Layer

**Files:**
- Create: `scoreboard/db.py`
- Create: `scoreboard/tests/test_db.py`

- [ ] **Step 1: Write failing tests for DB initialization and PIN operations**

```python
# scoreboard/tests/test_db.py
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone

import pytest

# Override DB path before importing db module
_tmp = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_PATH"] = _tmp

from scoreboard import db


@pytest.fixture(autouse=True)
def fresh_db():
    """Re-initialize DB for each test."""
    db.init_db(db_path=_tmp)
    yield
    if os.path.exists(_tmp):
        os.unlink(_tmp)


class TestPins:
    def test_create_and_verify_pin(self):
        pin_code = db.create_pin("student@lpnu.ua")
        assert len(pin_code) == 6
        assert pin_code.isdigit()

        result = db.verify_pin("student@lpnu.ua", pin_code)
        assert result is True

    def test_verify_wrong_pin(self):
        db.create_pin("student@lpnu.ua")
        result = db.verify_pin("student@lpnu.ua", "000000")
        assert result is False

    def test_pin_expires(self):
        pin_code = db.create_pin("student@lpnu.ua", expiry_minutes=0)
        # PIN with 0-minute expiry is already expired
        result = db.verify_pin("student@lpnu.ua", pin_code)
        assert result is False

    def test_pin_used_only_once(self):
        pin_code = db.create_pin("student@lpnu.ua")
        assert db.verify_pin("student@lpnu.ua", pin_code) is True
        # Second use should fail — PIN is consumed
        assert db.verify_pin("student@lpnu.ua", pin_code) is False


class TestSubmissions:
    def test_create_submission(self):
        sub_id = db.create_submission(
            email="student@lpnu.ua",
            name="Олександр",
            surname="Бауск",
            subgroup="ПЗ-21",
            param_a=21,
            hyperparameters='{"learning_rate": 0.001}',
            model_standard_path="/uploads/1/model_standard.zip",
            model_individual_path="/uploads/1/model_individual.zip",
        )
        assert sub_id is not None
        sub = db.get_submission(sub_id)
        assert sub["email"] == "student@lpnu.ua"
        assert sub["status"] == "pending"

    def test_resubmit_supersedes_old(self):
        id1 = db.create_submission(
            email="student@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21,
            hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        id2 = db.create_submission(
            email="student@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21,
            hyperparameters='{}',
            model_standard_path="/c", model_individual_path="/d",
        )
        old = db.get_submission(id1)
        assert old["superseded_by"] == id2

        active = db.get_active_submissions()
        emails = [s["email"] for s in active]
        assert emails.count("student@lpnu.ua") == 1

    def test_update_evaluation_results(self):
        sub_id = db.create_submission(
            email="s@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21,
            hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        db.update_evaluation(sub_id, standard_mean=210.5, standard_std=15.2,
                             individual_mean=180.0, individual_std=20.1)
        sub = db.get_submission(sub_id)
        assert sub["status"] == "done"
        assert sub["standard_mean"] == 210.5

    def test_update_evaluation_error(self):
        sub_id = db.create_submission(
            email="s@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21,
            hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        db.update_evaluation_error(sub_id, "Model file corrupt")
        sub = db.get_submission(sub_id)
        assert sub["status"] == "error"
        assert sub["error_message"] == "Model file corrupt"

    def test_get_pending_submissions(self):
        db.create_submission(
            email="s@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21,
            hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        pending = db.get_pending_submissions()
        assert len(pending) == 1
        assert pending[0]["status"] == "pending"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scoreboard && python -m pytest tests/test_db.py -v`
Expected: ImportError or AttributeError — `db` module doesn't exist yet.

- [ ] **Step 3: Implement db.py**

```python
# scoreboard/db.py
import json
import random
import sqlite3
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scoreboard import config

_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS pins (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL,
    pin         TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    expires_at  TEXT NOT NULL,
    used        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS submissions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    email                 TEXT NOT NULL,
    name                  TEXT NOT NULL,
    surname               TEXT NOT NULL,
    subgroup              TEXT NOT NULL,
    param_a               INTEGER NOT NULL,
    hyperparameters       TEXT NOT NULL,
    hyperparam_min_dist   REAL,
    model_standard_path   TEXT NOT NULL,
    model_individual_path TEXT NOT NULL,
    standard_mean         REAL,
    standard_std          REAL,
    individual_mean       REAL,
    individual_std        REAL,
    status                TEXT NOT NULL DEFAULT 'pending',
    error_message         TEXT,
    superseded_by         INTEGER,
    created_at            TEXT NOT NULL,
    evaluated_at          TEXT
);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_conn(db_path: str | None = None) -> sqlite3.Connection:
    global _conn
    if _conn is None:
        path = db_path or config.DATABASE_PATH
        _conn = sqlite3.connect(path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
    return _conn


def init_db(db_path: str | None = None):
    global _conn
    _conn = None  # Reset connection
    conn = get_conn(db_path)
    conn.executescript(SCHEMA)
    conn.commit()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── PIN operations ──

def create_pin(email: str, expiry_minutes: int | None = None) -> str:
    if expiry_minutes is None:
        expiry_minutes = config.PIN_EXPIRY_MINUTES
    pin = "".join(random.choices(string.digits, k=6))
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=expiry_minutes)
    conn = get_conn()
    conn.execute(
        "INSERT INTO pins (email, pin, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (email, pin, now.isoformat(), expires.isoformat()),
    )
    conn.commit()
    return pin


def verify_pin(email: str, pin: str) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT id, expires_at FROM pins WHERE email = ? AND pin = ? AND used = 0 ORDER BY created_at DESC LIMIT 1",
        (email, pin),
    ).fetchone()
    if row is None:
        return False
    expires = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires:
        return False
    conn.execute("UPDATE pins SET used = 1 WHERE id = ?", (row["id"],))
    conn.commit()
    return True


# ── Submission operations ──

def create_submission(
    email: str, name: str, surname: str, subgroup: str,
    param_a: int, hyperparameters: str,
    model_standard_path: str, model_individual_path: str,
) -> int:
    conn = get_conn()
    # Insert new submission
    cursor = conn.execute(
        """INSERT INTO submissions
        (email, name, surname, subgroup, param_a, hyperparameters,
         model_standard_path, model_individual_path, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (email, name, surname, subgroup, param_a, hyperparameters,
         model_standard_path, model_individual_path, _now_iso()),
    )
    new_id = cursor.lastrowid
    # Mark previous submissions from same email as superseded
    conn.execute(
        "UPDATE submissions SET superseded_by = ? WHERE email = ? AND id != ? AND superseded_by IS NULL",
        (new_id, email, new_id),
    )
    conn.commit()
    return new_id


def get_submission(sub_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (sub_id,)).fetchone()
    return dict(row) if row else None


def get_active_submissions() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM submissions WHERE superseded_by IS NULL ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def get_pending_submissions() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM submissions WHERE status IN ('pending', 'evaluating') AND superseded_by IS NULL ORDER BY created_at ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def set_status(sub_id: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE submissions SET status = ? WHERE id = ?", (status, sub_id))
    conn.commit()


def update_evaluation(sub_id: int, standard_mean: float, standard_std: float,
                      individual_mean: float, individual_std: float):
    conn = get_conn()
    conn.execute(
        """UPDATE submissions SET
            standard_mean = ?, standard_std = ?,
            individual_mean = ?, individual_std = ?,
            status = 'done', evaluated_at = ?
        WHERE id = ?""",
        (standard_mean, standard_std, individual_mean, individual_std, _now_iso(), sub_id),
    )
    conn.commit()


def update_evaluation_error(sub_id: int, error_message: str):
    conn = get_conn()
    conn.execute(
        "UPDATE submissions SET status = 'error', error_message = ?, evaluated_at = ? WHERE id = ?",
        (error_message, _now_iso(), sub_id),
    )
    conn.commit()


def update_hyperparam_distances(distances: dict[int, float | None]):
    """Update hyperparam_min_dist for multiple submissions by ID."""
    conn = get_conn()
    for sub_id, dist in distances.items():
        conn.execute(
            "UPDATE submissions SET hyperparam_min_dist = ? WHERE id = ?",
            (dist, sub_id),
        )
    conn.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scoreboard && python -m pytest tests/test_db.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scoreboard/db.py scoreboard/tests/test_db.py
git commit -m "feat(scoreboard): database layer with PIN and submission operations"
```

---

### Task 3: Scoring Formula

**Files:**
- Create: `scoreboard/scoring.py`
- Create: `scoreboard/tests/test_scoring.py`

- [ ] **Step 1: Write failing test**

```python
# scoreboard/tests/test_scoring.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scoreboard && python -m pytest tests/test_scoring.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement scoring.py**

```python
# scoreboard/scoring.py


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scoreboard && python -m pytest tests/test_scoring.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add scoreboard/scoring.py scoreboard/tests/test_scoring.py
git commit -m "feat(scoreboard): editable ranking formula"
```

---

### Task 4: Hyperparameter Distance

**Files:**
- Create: `scoreboard/hyperparams.py`
- Create: `scoreboard/tests/test_hyperparams.py`

- [ ] **Step 1: Write failing tests**

```python
# scoreboard/tests/test_hyperparams.py
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
    # After min-max normalization, each dimension spans [0, 1]
    # distance = sqrt(1^2 + 1^2) = sqrt(2)
    assert math.isclose(distances[1], math.sqrt(2), rel_tol=1e-6)
    assert math.isclose(distances[2], math.sqrt(2), rel_tol=1e-6)


def test_single_submission():
    subs = [
        {"id": 1, "hyperparameters": '{"learning_rate": 0.001}'},
    ]
    distances = compute_all_min_distances(subs)
    assert distances[1] is None  # No other submission to compare against


def test_three_submissions_min_distance():
    subs = [
        {"id": 1, "hyperparameters": '{"lr": 0.001}'},
        {"id": 2, "hyperparameters": '{"lr": 0.002}'},
        {"id": 3, "hyperparameters": '{"lr": 0.01}'},
    ]
    distances = compute_all_min_distances(subs)
    # After normalization: id1=0.0, id2=0.111, id3=1.0
    # min_dist for id1 = dist to id2
    # min_dist for id3 = dist to id2
    # min_dist for id2 = dist to id1 (closer than id3)
    assert distances[2] < distances[3]


def test_missing_keys_default_zero():
    subs = [
        {"id": 1, "hyperparameters": '{"lr": 0.001, "gamma": 0.99}'},
        {"id": 2, "hyperparameters": '{"lr": 0.001}'},
    ]
    distances = compute_all_min_distances(subs)
    # gamma dimension: id1=0.99, id2=0 → after normalization both extremes
    assert distances[1] > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scoreboard && python -m pytest tests/test_hyperparams.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement hyperparams.py**

```python
# scoreboard/hyperparams.py
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

    # Parse hyperparameters
    parsed = []
    all_keys: set[str] = set()
    for sub in submissions:
        params = json.loads(sub["hyperparameters"]) if sub["hyperparameters"] else {}
        # Only keep numeric values
        numeric = {k: float(v) for k, v in params.items() if isinstance(v, (int, float))}
        parsed.append((sub["id"], numeric))
        all_keys.update(numeric.keys())

    keys = sorted(all_keys)
    if not keys:
        return {sub_id: 0.0 for sub_id, _ in parsed}

    # Build raw vectors (missing keys default to 0)
    vectors: dict[int, list[float]] = {}
    for sub_id, params in parsed:
        vectors[sub_id] = [params.get(k, 0.0) for k in keys]

    # Min-max normalize each dimension
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

    # Pairwise Euclidean distances, store min
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scoreboard && python -m pytest tests/test_hyperparams.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add scoreboard/hyperparams.py scoreboard/tests/test_hyperparams.py
git commit -m "feat(scoreboard): hyperparameter distance calculation for plagiarism detection"
```

---

### Task 5: Email Service

**Files:**
- Create: `scoreboard/email_service.py`

- [ ] **Step 1: Implement email_service.py**

```python
# scoreboard/email_service.py
import resend

from scoreboard import config


def send_pin_email(to_email: str, pin: str):
    """Send a PIN verification email via Resend."""
    resend.api_key = config.RESEND_API_KEY

    resend.Emails.send({
        "from": config.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Код підтвердження для турнірної таблиці — ЛР №3",
        "text": (
            f"Ваш код підтвердження: {pin}\n\n"
            f"Код дійсний протягом {config.PIN_EXPIRY_MINUTES} хвилин.\n\n"
            "Якщо ви не запитували цей код, проігноруйте цей лист."
        ),
    })
```

- [ ] **Step 2: Commit**

```bash
git add scoreboard/email_service.py
git commit -m "feat(scoreboard): Resend email service for PIN delivery"
```

---

### Task 6: Background Evaluator

**Files:**
- Create: `scoreboard/evaluator.py`

This task reuses logic from the existing `labs-sources/ai-lab-2026-03/leaderboard_runner.py`. The evaluator depends on gymnasium and stable-baselines3 at runtime, so tests are deferred to the integration smoke test (Task 9).

- [ ] **Step 1: Implement evaluator.py**

```python
# scoreboard/evaluator.py
import logging
import queue
import threading
from pathlib import Path

from scoreboard import db
from scoreboard import config

logger = logging.getLogger(__name__)

_queue: queue.Queue[int] = queue.Queue()


def compute_individual_params(A: int) -> dict:
    """Compute individual environment parameters from student parameter A."""
    return {
        "gravity": -10.0 + (A % 5) * (-0.5),
        "enable_wind": A > 15,
        "wind_power": (A % 10) * 1.5,
        "turbulence_power": (A % 7) * 0.25,
    }


def _evaluate_model(model_path: str, env_kwargs: dict, n_episodes: int) -> dict:
    """Evaluate a single model. Imports SB3/gym lazily to keep module importable."""
    import gymnasium as gym
    from stable_baselines3 import DQN
    from stable_baselines3.common.evaluation import evaluate_policy

    model = DQN.load(model_path)
    env = gym.make("LunarLander-v3", **env_kwargs)
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=n_episodes, seed=0)
    env.close()
    return {"mean_reward": float(mean_reward), "std_reward": float(std_reward)}


def _worker():
    """Background worker thread — processes one submission at a time."""
    while True:
        sub_id = _queue.get()
        try:
            sub = db.get_submission(sub_id)
            if sub is None or sub["superseded_by"] is not None:
                continue

            logger.info(f"Evaluating submission {sub_id} ({sub['name']} {sub['surname']})")
            db.set_status(sub_id, "evaluating")

            n_episodes = config.EVALUATION_EPISODES

            # Standard environment
            std_result = _evaluate_model(sub["model_standard_path"], {}, n_episodes)

            # Individual environment
            ind_params = compute_individual_params(sub["param_a"])
            ind_result = _evaluate_model(sub["model_individual_path"], ind_params, n_episodes)

            db.update_evaluation(
                sub_id,
                standard_mean=std_result["mean_reward"],
                standard_std=std_result["std_reward"],
                individual_mean=ind_result["mean_reward"],
                individual_std=ind_result["std_reward"],
            )
            logger.info(f"Submission {sub_id} done: std={std_result['mean_reward']:.1f}, ind={ind_result['mean_reward']:.1f}")

        except Exception as e:
            logger.exception(f"Evaluation failed for submission {sub_id}")
            db.update_evaluation_error(sub_id, str(e))
        finally:
            _queue.task_done()


def enqueue(sub_id: int):
    """Add a submission to the evaluation queue."""
    _queue.put(sub_id)


def start():
    """Start the background evaluator thread. Re-queues any pending submissions."""
    pending = db.get_pending_submissions()
    for sub in pending:
        _queue.put(sub["id"])
    if pending:
        logger.info(f"Re-queued {len(pending)} pending submissions")

    t = threading.Thread(target=_worker, daemon=True, name="evaluator")
    t.start()
    logger.info("Background evaluator started")
```

- [ ] **Step 2: Commit**

```bash
git add scoreboard/evaluator.py
git commit -m "feat(scoreboard): background model evaluation worker"
```

---

### Task 7: FastAPI Application and API Routes

**Files:**
- Create: `scoreboard/main.py`
- Create: `scoreboard/__init__.py`
- Create: `scoreboard/tests/test_api.py`

- [ ] **Step 1: Create scoreboard/__init__.py**

Empty file — makes `scoreboard` a package.

- [ ] **Step 2: Write failing API tests**

```python
# scoreboard/tests/test_api.py
import io
import json
import os
import tempfile

import pytest

# Set up test DB before importing app
_tmp_db = tempfile.mktemp(suffix=".db")
_tmp_uploads = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = _tmp_db
os.environ["UPLOADS_DIR"] = _tmp_uploads
os.environ["RESEND_API_KEY"] = "test_key"

from fastapi.testclient import TestClient
from scoreboard import db
from scoreboard.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    db.init_db(db_path=_tmp_db)
    yield
    if os.path.exists(_tmp_db):
        os.unlink(_tmp_db)


class TestRequestPin:
    def test_valid_email(self, monkeypatch):
        # Mock email sending
        sent = []
        monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: sent.append((to, pin)))

        resp = client.post("/api/request-pin", json={"email": "student@lpnu.ua"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert len(sent) == 1
        assert sent[0][0] == "student@lpnu.ua"

    def test_invalid_email_domain(self):
        resp = client.post("/api/request-pin", json={"email": "student@gmail.com"})
        assert resp.status_code == 400

    def test_missing_email(self):
        resp = client.post("/api/request-pin", json={})
        assert resp.status_code == 422


class TestUpload:
    def _get_pin(self, monkeypatch, email="student@lpnu.ua"):
        monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: None)
        client.post("/api/request-pin", json={"email": email})
        # Retrieve PIN directly from DB
        conn = db.get_conn()
        row = conn.execute("SELECT pin FROM pins WHERE email = ? ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        return row["pin"]

    def test_successful_upload(self, monkeypatch):
        pin = self._get_pin(monkeypatch)
        resp = client.post(
            "/api/upload",
            data={
                "email": "student@lpnu.ua",
                "pin": pin,
                "name": "Олександр",
                "surname": "Бауск",
                "subgroup": "ПЗ-21",
                "param_a": "21",
                "hyperparameters": '{"learning_rate": 0.001}',
            },
            files={
                "model_standard": ("model_standard.zip", io.BytesIO(b"fake zip content"), "application/zip"),
                "model_individual": ("model_individual.zip", io.BytesIO(b"fake zip content"), "application/zip"),
            },
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert "submission_id" in resp.json()

    def test_wrong_pin(self, monkeypatch):
        self._get_pin(monkeypatch)
        resp = client.post(
            "/api/upload",
            data={
                "email": "student@lpnu.ua",
                "pin": "000000",
                "name": "О",
                "surname": "Б",
                "subgroup": "ПЗ-21",
                "param_a": "21",
                "hyperparameters": "{}",
            },
            files={
                "model_standard": ("m.zip", io.BytesIO(b"x"), "application/zip"),
                "model_individual": ("m.zip", io.BytesIO(b"x"), "application/zip"),
            },
        )
        assert resp.status_code == 403

    def test_invalid_subgroup(self, monkeypatch):
        pin = self._get_pin(monkeypatch)
        resp = client.post(
            "/api/upload",
            data={
                "email": "student@lpnu.ua",
                "pin": pin,
                "name": "О",
                "surname": "Б",
                "subgroup": "INVALID",
                "param_a": "21",
                "hyperparameters": "{}",
            },
            files={
                "model_standard": ("m.zip", io.BytesIO(b"x"), "application/zip"),
                "model_individual": ("m.zip", io.BytesIO(b"x"), "application/zip"),
            },
        )
        assert resp.status_code == 400


class TestScoreboard:
    def test_empty_scoreboard(self):
        resp = client.get("/api/scoreboard")
        assert resp.status_code == 200
        assert resp.json()["submissions"] == []
        assert isinstance(resp.json()["subgroups"], list)

    def test_scoreboard_with_submission(self, monkeypatch):
        monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: None)
        # Don't actually enqueue for evaluation in tests
        monkeypatch.setattr("scoreboard.evaluator.enqueue", lambda sub_id: None)

        pin = self._get_pin(monkeypatch)
        client.post(
            "/api/upload",
            data={
                "email": "student@lpnu.ua",
                "pin": pin,
                "name": "Олександр",
                "surname": "Бауск",
                "subgroup": "ПЗ-21",
                "param_a": "21",
                "hyperparameters": '{"learning_rate": 0.001}',
            },
            files={
                "model_standard": ("m.zip", io.BytesIO(b"x"), "application/zip"),
                "model_individual": ("m.zip", io.BytesIO(b"x"), "application/zip"),
            },
        )
        resp = client.get("/api/scoreboard")
        data = resp.json()
        assert len(data["submissions"]) == 1
        assert data["submissions"][0]["name"] == "Олександр"

    def _get_pin(self, monkeypatch, email="student@lpnu.ua"):
        monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: None)
        client.post("/api/request-pin", json={"email": email})
        conn = db.get_conn()
        row = conn.execute("SELECT pin FROM pins WHERE email = ? ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        return row["pin"]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd scoreboard && python -m pytest tests/test_api.py -v`
Expected: ImportError — `main.py` doesn't exist.

- [ ] **Step 4: Implement main.py**

```python
# scoreboard/main.py
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scoreboard import config, db, evaluator
from scoreboard.email_service import send_pin_email
from scoreboard.hyperparams import compute_all_min_distances
from scoreboard.scoring import compute_rank_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    evaluator.start()
    logger.info("Scoreboard started")
    yield


app = FastAPI(title="Lab 3 Scoreboard", lifespan=lifespan)

# Serve static files
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ── Models ──

class PinRequest(BaseModel):
    email: str


# ── Routes ──

@app.get("/")
async def index():
    return FileResponse(str(_static_dir / "index.html"))


@app.post("/api/request-pin")
async def request_pin(req: PinRequest):
    email = req.email.strip().lower()
    if not email.endswith("@lpnu.ua"):
        raise HTTPException(400, "Дозволені лише адреси @lpnu.ua")

    pin = db.create_pin(email)
    send_pin_email(email, pin)
    return {"ok": True, "message": "PIN надіслано на вашу пошту"}


@app.post("/api/upload")
async def upload(
    email: str = Form(...),
    pin: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    subgroup: str = Form(...),
    param_a: int = Form(...),
    hyperparameters: str = Form(...),
    model_standard: UploadFile = File(...),
    model_individual: UploadFile = File(...),
):
    email = email.strip().lower()

    # Validate email
    if not email.endswith("@lpnu.ua"):
        raise HTTPException(400, "Дозволені лише адреси @lpnu.ua")

    # Validate PIN
    if not db.verify_pin(email, pin):
        raise HTTPException(403, "Невірний або прострочений PIN")

    # Validate subgroup
    if subgroup not in config.SUBGROUPS:
        raise HTTPException(400, f"Невідома підгрупа: {subgroup}")

    # Validate hyperparameters is valid JSON
    try:
        json.loads(hyperparameters)
    except json.JSONDecodeError:
        raise HTTPException(400, "Гіперпараметри повинні бути валідним JSON")

    # Validate file names end with .zip
    for f, label in [(model_standard, "model_standard"), (model_individual, "model_individual")]:
        if not f.filename.endswith(".zip"):
            raise HTTPException(400, f"{label} повинен бути .zip файлом")

    # Create submission to get ID
    sub_id = db.create_submission(
        email=email, name=name, surname=surname, subgroup=subgroup,
        param_a=param_a, hyperparameters=hyperparameters,
        model_standard_path="",  # placeholder, update after saving files
        model_individual_path="",
    )

    # Save files
    upload_dir = config.UPLOADS_DIR / str(sub_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    std_path = upload_dir / "model_standard.zip"
    ind_path = upload_dir / "model_individual.zip"

    std_content = await model_standard.read()
    ind_content = await model_individual.read()

    # Check file size
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
    for content, label in [(std_content, "model_standard"), (ind_content, "model_individual")]:
        if len(content) > max_bytes:
            raise HTTPException(400, f"{label} перевищує ліміт {config.MAX_FILE_SIZE_MB}MB")

    std_path.write_bytes(std_content)
    ind_path.write_bytes(ind_content)

    # Update file paths in DB
    conn = db.get_conn()
    conn.execute(
        "UPDATE submissions SET model_standard_path = ?, model_individual_path = ? WHERE id = ?",
        (str(std_path), str(ind_path), sub_id),
    )
    conn.commit()

    # Recompute hyperparameter distances for all active submissions
    active = db.get_active_submissions()
    distances = compute_all_min_distances(active)
    db.update_hyperparam_distances(distances)

    # Enqueue for evaluation
    evaluator.enqueue(sub_id)

    return {"ok": True, "submission_id": sub_id, "message": "Модель завантажено, очікуйте оцінку"}


@app.get("/api/scoreboard")
async def scoreboard():
    active = db.get_active_submissions()

    # Attach rank_score
    for sub in active:
        sub["rank_score"] = compute_rank_score(sub)

    return {
        "subgroups": config.SUBGROUPS,
        "submissions": active,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scoreboard.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scoreboard && python -m pytest tests/test_api.py -v`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add scoreboard/__init__.py scoreboard/main.py scoreboard/tests/test_api.py
git commit -m "feat(scoreboard): FastAPI app with PIN, upload, and scoreboard endpoints"
```

---

### Task 8: Frontend

**Files:**
- Create: `scoreboard/static/index.html`
- Create: `scoreboard/static/style.css`
- Create: `scoreboard/static/app.js`

- [ ] **Step 1: Create index.html**

```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Турнірна таблиця — ЛР №3</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>Турнірна таблиця — Лабораторна робота №3</h1>
        <p class="subtitle">LunarLander DQN — Навчання з підкріпленням</p>

        <!-- Upload Section -->
        <section id="upload-section">
            <h2>Завантажити модель</h2>

            <!-- Step 1: Email -->
            <div id="step-email">
                <label for="email">Email (@lpnu.ua):</label>
                <input type="email" id="email" placeholder="student@lpnu.ua">
                <button id="btn-request-pin">Отримати PIN</button>
                <p id="email-status" class="status"></p>
            </div>

            <!-- Step 2: Full form (hidden until PIN sent) -->
            <div id="step-upload" class="hidden">
                <div class="form-grid">
                    <div>
                        <label for="pin">PIN-код:</label>
                        <input type="text" id="pin" maxlength="6" placeholder="123456">
                    </div>
                    <div>
                        <label for="name">Ім'я:</label>
                        <input type="text" id="name" placeholder="Олександр">
                    </div>
                    <div>
                        <label for="surname">Прізвище:</label>
                        <input type="text" id="surname" placeholder="Бауск">
                    </div>
                    <div>
                        <label for="subgroup">Підгрупа:</label>
                        <select id="subgroup"></select>
                    </div>
                    <div>
                        <label for="param_a">Параметр A:</label>
                        <input type="number" id="param_a" min="2" max="66">
                    </div>
                    <div class="full-width">
                        <label for="hyperparameters">Гіперпараметри (JSON):</label>
                        <textarea id="hyperparameters" rows="3" placeholder='{"learning_rate": 0.001, "buffer_size": 50000}'></textarea>
                    </div>
                    <div>
                        <label for="model_standard">model_standard.zip:</label>
                        <input type="file" id="model_standard" accept=".zip">
                    </div>
                    <div>
                        <label for="model_individual">model_individual.zip:</label>
                        <input type="file" id="model_individual" accept=".zip">
                    </div>
                </div>
                <button id="btn-upload">Завантажити</button>
                <p id="upload-status" class="status"></p>
            </div>
        </section>

        <!-- Scoreboard Section -->
        <section id="scoreboard-section">
            <h2>Рейтинг</h2>
            <button id="btn-refresh">Оновити</button>
            <div id="scoreboard-tabs"></div>
            <div id="scoreboard-content"></div>
        </section>
    </div>
    <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create style.css**

```css
/* scoreboard/static/style.css */
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 960px;
    margin: 2rem auto;
    padding: 0 1rem;
}

h1 { margin-bottom: 0.25rem; }
.subtitle { color: #666; margin-bottom: 2rem; }
h2 { margin: 1.5rem 0 1rem; }

section {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

label { display: block; font-weight: 600; margin: 0.5rem 0 0.25rem; }

input, select, textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
}

button {
    margin-top: 1rem;
    padding: 0.6rem 1.5rem;
    background: #2563eb;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
}
button:hover { background: #1d4ed8; }
button:disabled { background: #94a3b8; cursor: not-allowed; }

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
.form-grid .full-width { grid-column: 1 / -1; }

.hidden { display: none; }

.status { margin-top: 0.5rem; font-weight: 600; }
.status.ok { color: #16a34a; }
.status.err { color: #dc2626; }

/* Tabs */
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.tab {
    padding: 0.4rem 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    background: #fff;
    font-size: 0.9rem;
}
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; }

/* Table */
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f8fafc; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: #555; }
tr:hover { background: #f8fafc; }

.score-good { color: #16a34a; font-weight: 600; }
.score-mid { color: #ca8a04; }
.score-bad { color: #dc2626; }

.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-pending { background: #fef3c7; color: #92400e; }
.badge-evaluating { background: #dbeafe; color: #1e40af; }
.badge-done { background: #dcfce7; color: #166534; }
.badge-error { background: #fecaca; color: #991b1b; }
```

- [ ] **Step 3: Create app.js**

```javascript
// scoreboard/static/app.js

const API = "";

// ── State ──
let subgroups = [];
let submissions = [];
let activeTab = null;

// ── DOM refs ──
const $ = (id) => document.getElementById(id);

// ── Init ──
document.addEventListener("DOMContentLoaded", () => {
    loadScoreboard();

    $("btn-request-pin").addEventListener("click", requestPin);
    $("btn-upload").addEventListener("click", uploadSubmission);
    $("btn-refresh").addEventListener("click", loadScoreboard);
});

// ── Email / PIN ──
async function requestPin() {
    const email = $("email").value.trim().toLowerCase();
    const status = $("email-status");

    if (!email.endsWith("@lpnu.ua")) {
        status.textContent = "Дозволені лише адреси @lpnu.ua";
        status.className = "status err";
        return;
    }

    $("btn-request-pin").disabled = true;
    status.textContent = "Надсилаємо...";
    status.className = "status";

    try {
        const resp = await fetch(`${API}/api/request-pin`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
        });
        const data = await resp.json();
        if (resp.ok) {
            status.textContent = "PIN надіслано на вашу пошту!";
            status.className = "status ok";
            $("step-upload").classList.remove("hidden");
        } else {
            status.textContent = data.detail || "Помилка";
            status.className = "status err";
        }
    } catch (e) {
        status.textContent = "Помилка мережі";
        status.className = "status err";
    } finally {
        $("btn-request-pin").disabled = false;
    }
}

// ── Upload ──
async function uploadSubmission() {
    const status = $("upload-status");
    const btn = $("btn-upload");

    // Validate JSON
    const hpText = $("hyperparameters").value.trim();
    try {
        JSON.parse(hpText);
    } catch {
        status.textContent = "Гіперпараметри — невалідний JSON";
        status.className = "status err";
        return;
    }

    const formData = new FormData();
    formData.append("email", $("email").value.trim().toLowerCase());
    formData.append("pin", $("pin").value.trim());
    formData.append("name", $("name").value.trim());
    formData.append("surname", $("surname").value.trim());
    formData.append("subgroup", $("subgroup").value);
    formData.append("param_a", $("param_a").value);
    formData.append("hyperparameters", hpText);
    formData.append("model_standard", $("model_standard").files[0]);
    formData.append("model_individual", $("model_individual").files[0]);

    btn.disabled = true;
    status.textContent = "Завантажуємо...";
    status.className = "status";

    try {
        const resp = await fetch(`${API}/api/upload`, {
            method: "POST",
            body: formData,
        });
        const data = await resp.json();
        if (resp.ok) {
            status.textContent = "Модель завантажено! Оцінка розпочнеться автоматично.";
            status.className = "status ok";
            loadScoreboard();
        } else {
            status.textContent = data.detail || "Помилка завантаження";
            status.className = "status err";
        }
    } catch (e) {
        status.textContent = "Помилка мережі";
        status.className = "status err";
    } finally {
        btn.disabled = false;
    }
}

// ── Scoreboard ──
async function loadScoreboard() {
    try {
        const resp = await fetch(`${API}/api/scoreboard`);
        const data = await resp.json();
        subgroups = data.subgroups;
        submissions = data.submissions;

        populateSubgroupDropdown();
        renderTabs();
        renderTable();
    } catch (e) {
        $("scoreboard-content").innerHTML = "<p>Помилка завантаження рейтингу</p>";
    }
}

function populateSubgroupDropdown() {
    const sel = $("subgroup");
    sel.innerHTML = "";
    subgroups.forEach((sg) => {
        const opt = document.createElement("option");
        opt.value = sg;
        opt.textContent = sg;
        sel.appendChild(opt);
    });
}

function renderTabs() {
    // Collect all subgroups that have submissions (including old ones not in active list)
    const allGroups = new Set([...subgroups]);
    submissions.forEach((s) => allGroups.add(s.subgroup));

    const tabsEl = $("scoreboard-tabs");
    tabsEl.innerHTML = "";
    tabsEl.className = "tabs";

    // "All" tab
    const allTab = document.createElement("div");
    allTab.className = "tab" + (activeTab === null ? " active" : "");
    allTab.textContent = "Усі";
    allTab.addEventListener("click", () => { activeTab = null; renderTabs(); renderTable(); });
    tabsEl.appendChild(allTab);

    [...allGroups].sort().forEach((sg) => {
        const tab = document.createElement("div");
        tab.className = "tab" + (activeTab === sg ? " active" : "");
        tab.textContent = sg;
        tab.addEventListener("click", () => { activeTab = sg; renderTabs(); renderTable(); });
        tabsEl.appendChild(tab);
    });
}

function renderTable() {
    const filtered = activeTab
        ? submissions.filter((s) => s.subgroup === activeTab)
        : submissions;

    // Sort by rank_score descending
    const sorted = [...filtered].sort((a, b) => (b.rank_score ?? -Infinity) - (a.rank_score ?? -Infinity));

    if (sorted.length === 0) {
        $("scoreboard-content").innerHTML = "<p>Немає результатів</p>";
        return;
    }

    let html = `<table>
        <thead><tr>
            <th>#</th>
            <th>Ім'я</th>
            <th>Підгрупа</th>
            <th>Стандарт</th>
            <th>Індивід.</th>
            <th>Рейтинг</th>
            <th>Статус</th>
            <th>Схожість</th>
        </tr></thead><tbody>`;

    sorted.forEach((s, i) => {
        const rank = i + 1;
        const stdScore = formatScore(s.standard_mean);
        const indScore = formatScore(s.individual_mean);
        const rankScore = s.rank_score != null ? s.rank_score.toFixed(1) : "—";
        const statusBadge = `<span class="badge badge-${s.status}">${statusLabel(s.status)}</span>`;
        const dist = s.hyperparam_min_dist != null ? s.hyperparam_min_dist.toFixed(3) : "—";

        html += `<tr>
            <td>${rank}</td>
            <td>${escHtml(s.name)} ${escHtml(s.surname)}</td>
            <td>${escHtml(s.subgroup)}</td>
            <td class="${scoreClass(s.standard_mean)}">${stdScore}</td>
            <td class="${scoreClass(s.individual_mean)}">${indScore}</td>
            <td><strong>${rankScore}</strong></td>
            <td>${statusBadge}</td>
            <td>${dist}</td>
        </tr>`;
    });

    html += "</tbody></table>";
    $("scoreboard-content").innerHTML = html;
}

// ── Helpers ──
function formatScore(val) {
    if (val == null) return "—";
    return val.toFixed(1);
}

function scoreClass(val) {
    if (val == null) return "";
    if (val >= 200) return "score-good";
    if (val >= 0) return "score-mid";
    return "score-bad";
}

function statusLabel(status) {
    const labels = { pending: "Очікує", evaluating: "Оцінюється", done: "Готово", error: "Помилка" };
    return labels[status] || status;
}

function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
```

- [ ] **Step 4: Verify frontend loads**

Run: `cd scoreboard && python -m scoreboard.main`

Open `http://localhost:8000` in browser. Confirm the page loads with the upload form and empty scoreboard.

- [ ] **Step 5: Commit**

```bash
git add scoreboard/static/
git commit -m "feat(scoreboard): frontend with upload form and scoreboard display"
```

---

### Task 9: Integration Smoke Test

**Files:** none new — manual verification

- [ ] **Step 1: Run all unit tests**

Run: `cd scoreboard && python -m pytest tests/ -v`
Expected: All PASS.

- [ ] **Step 2: Start the server**

Run: `cd scoreboard && RESEND_API_KEY=test python -m scoreboard.main`

Verify server starts without errors on `http://localhost:8000`.

- [ ] **Step 3: Test PIN flow manually (with real Resend key)**

Create a `.env` file with your real `RESEND_API_KEY`, run the server, request a PIN for a test `@lpnu.ua` email. Confirm email arrives.

- [ ] **Step 4: Test upload with dummy .zip files**

Upload two small `.zip` files through the form. Confirm:
- Submission appears on scoreboard with status "pending" or "evaluating"
- Files saved under `uploads/<id>/`

- [ ] **Step 5: Test evaluation with real models (optional)**

If you have trained models available, upload them and confirm evaluation completes and scores appear.

- [ ] **Step 6: Final commit**

```bash
git add -A scoreboard/
git commit -m "feat(scoreboard): complete Lab 3 scoreboard application"
```

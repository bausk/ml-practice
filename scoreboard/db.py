import json
import random
import sqlite3
import string
from datetime import datetime, timedelta, timezone

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
    _conn = None
    conn = get_conn(db_path)
    conn.executescript(SCHEMA)
    conn.commit()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def create_submission(email, name, surname, subgroup, param_a, hyperparameters, model_standard_path, model_individual_path) -> int:
    conn = get_conn()
    cursor = conn.execute(
        """INSERT INTO submissions
        (email, name, surname, subgroup, param_a, hyperparameters,
         model_standard_path, model_individual_path, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (email, name, surname, subgroup, param_a, hyperparameters,
         model_standard_path, model_individual_path, _now_iso()),
    )
    new_id = cursor.lastrowid
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
    conn = get_conn()
    for sub_id, dist in distances.items():
        conn.execute(
            "UPDATE submissions SET hyperparam_min_dist = ? WHERE id = ?",
            (dist, sub_id),
        )
    conn.commit()

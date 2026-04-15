import json
import random
import string
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, urlunparse

import psycopg2
import psycopg2.extras

from scoreboard import config

_conn: psycopg2.extensions.connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS pins (
    id          SERIAL PRIMARY KEY,
    email       TEXT NOT NULL,
    pin         TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    expires_at  TEXT NOT NULL,
    used        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS submissions (
    id                    SERIAL PRIMARY KEY,
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
    evaluated_at          TEXT,
    video_path            TEXT
);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _db_name_from_url(url: str) -> str:
    return urlparse(url).path.lstrip("/")


def _server_url(url: str) -> str:
    """Return connection URL pointing to the 'postgres' maintenance database."""
    parsed = urlparse(url)
    return urlunparse(parsed._replace(path="/postgres"))


def _ensure_database_exists(url: str):
    """Create the target database if it does not exist."""
    db_name = _db_name_from_url(url)
    server_url = _server_url(url)
    conn = psycopg2.connect(server_url)
    conn.autocommit = True
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{db_name}"')
        cur.close()
    finally:
        conn.close()


def get_conn(db_url: str | None = None) -> psycopg2.extensions.connection:
    global _conn
    if _conn is None or _conn.closed:
        url = db_url or config.DATABASE_URL
        _conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        _conn.autocommit = False
    return _conn


def init_db(db_url: str | None = None):
    global _conn
    _conn = None
    url = db_url or config.DATABASE_URL
    _ensure_database_exists(url)
    conn = get_conn(url)
    with conn.cursor() as cur:
        for statement in SCHEMA.split(";"):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
    conn.commit()

    # Migrations — idempotent
    with conn.cursor() as cur:
        cur.execute(
            "ALTER TABLE submissions ADD COLUMN IF NOT EXISTS video_path TEXT"
        )
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
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pins (email, pin, created_at, expires_at) VALUES (%s, %s, %s, %s)",
            (email, pin, now.isoformat(), expires.isoformat()),
        )
    conn.commit()
    return pin


def verify_pin(email: str, pin: str) -> bool:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, expires_at FROM pins WHERE email = %s AND pin = %s AND used = 0 ORDER BY created_at DESC LIMIT 1",
            (email, pin),
        )
        row = cur.fetchone()
    if row is None:
        return False
    row = dict(row)  # type: ignore[arg-type]
    expires = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) > expires:
        return False
    with conn.cursor() as cur:
        cur.execute("UPDATE pins SET used = 1 WHERE id = %s", (row["id"],))
    conn.commit()
    return True


def check_cooldown(email: str) -> tuple[bool, int]:
    """Check if the email is in a cooldown period after a submission.

    Returns (is_in_cooldown, remaining_seconds).
    """
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT created_at FROM submissions WHERE email = %s ORDER BY created_at DESC LIMIT 1",
            (email,),
        )
        row = cur.fetchone()
    if row is None:
        return False, 0
    last_submission = datetime.fromisoformat(dict(row)["created_at"])  # type: ignore[arg-type]
    cooldown_end = last_submission + timedelta(minutes=config.UPLOAD_COOLDOWN_MINUTES)
    now = datetime.now(timezone.utc)
    if now < cooldown_end:
        remaining = int((cooldown_end - now).total_seconds())
        return True, remaining
    return False, 0


def create_submission(email, name, surname, subgroup, param_a, hyperparameters, model_standard_path, model_individual_path) -> int:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO submissions
            (email, name, surname, subgroup, param_a, hyperparameters,
             model_standard_path, model_individual_path, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING id""",
            (email, name, surname, subgroup, param_a, hyperparameters,
             model_standard_path, model_individual_path, _now_iso()),
        )
        new_id: int = dict(cur.fetchone())["id"]  # type: ignore[arg-type]
        cur.execute(
            "UPDATE submissions SET superseded_by = %s WHERE email = %s AND id != %s AND superseded_by IS NULL",
            (new_id, email, new_id),
        )
    conn.commit()
    return new_id


def get_submission(sub_id: int) -> dict | None:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM submissions WHERE id = %s", (sub_id,))
        row = cur.fetchone()
    return dict(row) if row else None


def get_all_submissions() -> list[dict]:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM submissions ORDER BY created_at DESC"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_active_submissions() -> list[dict]:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM submissions WHERE superseded_by IS NULL ORDER BY created_at DESC"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_pending_submissions() -> list[dict]:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM submissions WHERE status IN ('pending', 'evaluating') AND superseded_by IS NULL ORDER BY created_at ASC"
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def set_status(sub_id: int, status: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("UPDATE submissions SET status = %s WHERE id = %s", (status, sub_id))
    conn.commit()


def update_evaluation(sub_id: int, standard_mean: float, standard_std: float,
                      individual_mean: float, individual_std: float):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE submissions SET
                standard_mean = %s, standard_std = %s,
                individual_mean = %s, individual_std = %s,
                status = 'done', evaluated_at = %s
            WHERE id = %s""",
            (standard_mean, standard_std, individual_mean, individual_std, _now_iso(), sub_id),
        )
    conn.commit()


def update_evaluation_error(sub_id: int, error_message: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE submissions SET status = 'error', error_message = %s, evaluated_at = %s WHERE id = %s",
            (error_message, _now_iso(), sub_id),
        )
    conn.commit()


def update_video_path(sub_id: int, video_path: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE submissions SET video_path = %s WHERE id = %s",
            (video_path, sub_id),
        )
    conn.commit()


def update_hyperparam_distances(distances: dict[int, float | None]):
    conn = get_conn()
    with conn.cursor() as cur:
        for sub_id, dist in distances.items():
            cur.execute(
                "UPDATE submissions SET hyperparam_min_dist = %s WHERE id = %s",
                (dist, sub_id),
            )
    conn.commit()

import io
import os

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")

if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL not set", allow_module_level=True)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from fastapi.testclient import TestClient
from scoreboard import db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    db.init_db(db_url=TEST_DATABASE_URL)
    yield
    conn = db.get_conn()
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS submissions, pins, config")
    conn.commit()
    db._conn = None


def _get_pin(monkeypatch, email="student@lpnu.ua"):
    monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: None)
    client.post("/api/request-pin", json={"email": email})
    conn = db.get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pin FROM pins WHERE email = %s ORDER BY id DESC LIMIT 1", (email,)
        )
        row = cur.fetchone()
    return row["pin"]


def _make_upload(monkeypatch, email="student@lpnu.ua", pin=None):
    monkeypatch.setattr("scoreboard.evaluator.enqueue", lambda sub_id: None)
    if pin is None:
        pin = _get_pin(monkeypatch, email)
    return client.post(
        "/api/upload",
        data={
            "email": email,
            "pin": pin,
            "name": "Олександр",
            "surname": "Тест",
            "subgroup": "ПЗ-33-1",
            "param_a": "5",
            "hyperparameters": '{"learning_rate": 0.001}',
        },
        files={
            "model_standard": (
                "model_standard.zip",
                io.BytesIO(b"PK\x05\x06" + b"\x00" * 18),
                "application/zip",
            ),
            "model_individual": (
                "model_individual.zip",
                io.BytesIO(b"PK\x05\x06" + b"\x00" * 18),
                "application/zip",
            ),
        },
    )


class TestVideoEndpoint:
    def test_video_not_found_when_no_video(self, monkeypatch):
        resp = _make_upload(monkeypatch)
        assert resp.status_code == 200
        sub_id = resp.json()["submission_id"]
        video_resp = client.get(f"/api/video/{sub_id}")
        assert video_resp.status_code == 404

    def test_video_not_found_for_unknown_id(self):
        resp = client.get("/api/video/99999")
        assert resp.status_code == 404

    def test_scoreboard_has_video_false_when_no_video(self, monkeypatch):
        upload_resp = _make_upload(monkeypatch)
        assert upload_resp.status_code == 200
        sub_id = upload_resp.json()["submission_id"]
        resp = client.get("/api/scoreboard")
        data = resp.json()
        submission = next(s for s in data["submissions"] if s["id"] == sub_id)
        assert submission["has_video"] is False

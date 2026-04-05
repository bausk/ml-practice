import io
import json
import os
import tempfile

import pytest

_tmp_db = tempfile.mktemp(suffix=".db")
_tmp_uploads = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = _tmp_db
os.environ["UPLOADS_DIR"] = _tmp_uploads
os.environ["RESEND_API_KEY"] = "test_key"

from fastapi.testclient import TestClient
from scoreboard import db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    db.init_db(db_path=_tmp_db)
    yield
    if os.path.exists(_tmp_db):
        os.unlink(_tmp_db)


def _get_pin(monkeypatch, email="student@lpnu.ua"):
    monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: None)
    client.post("/api/request-pin", json={"email": email})
    conn = db.get_conn()
    row = conn.execute("SELECT pin FROM pins WHERE email = ? ORDER BY id DESC LIMIT 1", (email,)).fetchone()
    return row["pin"]


class TestRequestPin:
    def test_valid_email(self, monkeypatch):
        sent = []
        monkeypatch.setattr("scoreboard.email_service.send_pin_email", lambda to, pin: sent.append((to, pin)))
        resp = client.post("/api/request-pin", json={"email": "student@lpnu.ua"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert len(sent) == 1

    def test_invalid_email_domain(self):
        resp = client.post("/api/request-pin", json={"email": "student@gmail.com"})
        assert resp.status_code == 400

    def test_missing_email(self):
        resp = client.post("/api/request-pin", json={})
        assert resp.status_code == 422


class TestUpload:
    def test_successful_upload(self, monkeypatch):
        monkeypatch.setattr("scoreboard.evaluator.enqueue", lambda sub_id: None)
        pin = _get_pin(monkeypatch)
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
        _get_pin(monkeypatch)
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
        monkeypatch.setattr("scoreboard.evaluator.enqueue", lambda sub_id: None)
        pin = _get_pin(monkeypatch)
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

    def test_scoreboard_with_submission(self, monkeypatch):
        monkeypatch.setattr("scoreboard.evaluator.enqueue", lambda sub_id: None)
        pin = _get_pin(monkeypatch)
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

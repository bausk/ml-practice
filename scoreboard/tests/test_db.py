import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

_tmp = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_PATH"] = _tmp

from scoreboard import db


@pytest.fixture(autouse=True)
def fresh_db():
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
        result = db.verify_pin("student@lpnu.ua", pin_code)
        assert result is False

    def test_pin_used_only_once(self):
        pin_code = db.create_pin("student@lpnu.ua")
        assert db.verify_pin("student@lpnu.ua", pin_code) is True
        assert db.verify_pin("student@lpnu.ua", pin_code) is False


class TestSubmissions:
    def test_create_submission(self):
        sub_id = db.create_submission(
            email="student@lpnu.ua", name="Олександр", surname="Бауск",
            subgroup="ПЗ-21", param_a=21,
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
            subgroup="ПЗ-21", param_a=21, hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        id2 = db.create_submission(
            email="student@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21, hyperparameters='{}',
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
            subgroup="ПЗ-21", param_a=21, hyperparameters='{}',
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
            subgroup="ПЗ-21", param_a=21, hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        db.update_evaluation_error(sub_id, "Model file corrupt")
        sub = db.get_submission(sub_id)
        assert sub["status"] == "error"
        assert sub["error_message"] == "Model file corrupt"

    def test_get_pending_submissions(self):
        db.create_submission(
            email="s@lpnu.ua", name="О", surname="Б",
            subgroup="ПЗ-21", param_a=21, hyperparameters='{}',
            model_standard_path="/a", model_individual_path="/b",
        )
        pending = db.get_pending_submissions()
        assert len(pending) == 1
        assert pending[0]["status"] == "pending"

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scoreboard import config, db, evaluator, email_service
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
    email_service.send_pin_email(email, pin)
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

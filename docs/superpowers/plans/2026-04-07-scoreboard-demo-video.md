# Scoreboard Demo Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After evaluating a student's individual model, record a short MP4 demo video and display it as a modal triggered by a button in the scoreboard table row.

**Architecture:** The background evaluator records one episode from the individual model using `render_mode="rgb_array"`, writes frames to `uploads/{sub_id}/demo_individual.mp4` via `imageio-ffmpeg`, and stores the local path in a new `video_path` DB column. A new FastAPI route `/api/video/{sub_id}` serves the file. The scoreboard API exposes `has_video` boolean so the frontend can show a button that opens a `<video>` modal.

**Tech Stack:** Python/FastAPI, gymnasium LunarLander-v3 rgb_array rendering, imageio[ffmpeg] for MP4 encoding, vanilla JS/HTML modal, PostgreSQL (ALTER TABLE migration).

---

## File Map

| File | Change |
|------|--------|
| `scoreboard/requirements.txt` | Add `imageio[ffmpeg]>=2.34` |
| `scoreboard/scoreboard/db.py` | Add `video_path TEXT` column migration in `init_db`, add `update_video_path()` |
| `scoreboard/scoreboard/evaluator.py` | Add `_record_video()`, call it after individual eval |
| `scoreboard/main.py` | Add `GET /api/video/{sub_id}` route; add `has_video` field to scoreboard response |
| `scoreboard/static/index.html` | Add modal `<div>` + `<video>` element |
| `scoreboard/static/style.css` | Add modal overlay styles |
| `scoreboard/static/app.js` | Add "Відео" column with button; open/close modal |
| `scoreboard/tests/test_db.py` | Test `update_video_path`, test migration idempotency |
| `scoreboard/tests/test_api.py` | Test `/api/video/{sub_id}` 404 and 200 cases |

---

## Task 1: Add imageio dependency

**Files:**
- Modify: `scoreboard/requirements.txt`

- [ ] **Step 1: Add dependency**

```
imageio[ffmpeg]>=2.34
```

Add as a new line in `requirements.txt` after the `numpy` line.

- [ ] **Step 2: Verify install locally**

```bash
cd scoreboard && pip install imageio[ffmpeg]
```

Expected: installs `imageio` and `imageio-ffmpeg` (bundled ffmpeg binary, no system dep needed).

- [ ] **Step 3: Commit**

```bash
git add scoreboard/requirements.txt
git commit -m "feat: add imageio[ffmpeg] for video recording"
```

---

## Task 2: DB migration — add video_path column

**Files:**
- Modify: `scoreboard/scoreboard/db.py`
- Test: `scoreboard/tests/test_db.py`

- [ ] **Step 1: Write the failing test**

Add to `scoreboard/tests/test_db.py` (inside a new `class TestVideoPath:`):

```python
class TestVideoPath:
    def test_video_path_column_exists_after_init(self):
        conn = db.get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='submissions' AND column_name='video_path'"
            )
            row = cur.fetchone()
        assert row is not None, "video_path column should exist after init_db"

    def test_update_video_path(self):
        sub_id = db.create_submission(
            email="a@lpnu.ua", name="A", surname="B", subgroup="ПЗ-33-1",
            param_a=5, hyperparameters="{}", model_standard_path="/tmp/s.zip",
            model_individual_path="/tmp/i.zip",
        )
        db.update_video_path(sub_id, "/uploads/1/demo_individual.mp4")
        sub = db.get_submission(sub_id)
        assert sub["video_path"] == "/uploads/1/demo_individual.mp4"

    def test_update_video_path_none(self):
        sub_id = db.create_submission(
            email="b@lpnu.ua", name="C", surname="D", subgroup="ПЗ-33-1",
            param_a=5, hyperparameters="{}", model_standard_path="/tmp/s.zip",
            model_individual_path="/tmp/i.zip",
        )
        sub = db.get_submission(sub_id)
        assert sub.get("video_path") is None
```

- [ ] **Step 2: Run to verify failure**

```bash
cd scoreboard && python -m pytest tests/test_db.py::TestVideoPath -v
```

Expected: `AttributeError: module 'scoreboard.db' has no attribute 'update_video_path'`

- [ ] **Step 3: Add migration and function to db.py**

In `db.py`, add `video_path TEXT` to `SCHEMA` (in `CREATE TABLE submissions`) AND add a migration in `init_db` so existing databases get the column:

In the `SCHEMA` constant, add `video_path TEXT,` after `evaluated_at TEXT`:
```python
    evaluated_at          TEXT,
    video_path            TEXT
```

In `init_db()`, after `conn.commit()`, add:
```python
    # Migrations — idempotent
    with conn.cursor() as cur:
        cur.execute(
            "ALTER TABLE submissions ADD COLUMN IF NOT EXISTS video_path TEXT"
        )
    conn.commit()
```

Add new function after `update_evaluation_error`:
```python
def update_video_path(sub_id: int, video_path: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE submissions SET video_path = %s WHERE id = %s",
            (video_path, sub_id),
        )
    conn.commit()
```

- [ ] **Step 4: Run tests**

```bash
cd scoreboard && python -m pytest tests/test_db.py::TestVideoPath -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add scoreboard/scoreboard/db.py scoreboard/tests/test_db.py
git commit -m "feat: add video_path column to submissions + update_video_path()"
```

---

## Task 3: Video recording in evaluator

**Files:**
- Modify: `scoreboard/scoreboard/evaluator.py`

Note: There are no unit tests for video recording because it requires a display and real gymnasium rendering. The integration is verified manually. However, we guard against failure so evaluation still succeeds if video generation fails.

- [ ] **Step 1: Add `_record_video()` to evaluator.py**

Add this function after `_evaluate_model`:

```python
def _record_video(model_path: str, env_kwargs: dict, output_path: str, seed: int = 42) -> None:
    """Record one deterministic episode as MP4. Requires imageio[ffmpeg]."""
    import imageio
    import gymnasium as gym
    from stable_baselines3 import DQN

    model = DQN.load(model_path)
    env = gym.make("LunarLander-v3", render_mode="rgb_array", **env_kwargs)
    frames = []
    obs, _ = env.reset(seed=seed)
    terminated, truncated = False, False
    while not (terminated or truncated):
        frames.append(env.render())
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
    frames.append(env.render())
    env.close()
    imageio.mimsave(output_path, frames, fps=30, macro_block_size=1)
```

- [ ] **Step 2: Call `_record_video` in `_worker()` after individual evaluation**

In `_worker()`, after the `db.update_evaluation(...)` call, add:

```python
            # Record demo video for individual model (best-effort)
            video_path = str(config.UPLOADS_DIR / str(sub_id) / "demo_individual.mp4")
            try:
                _record_video(sub["model_individual_path"], ind_params, video_path)
                db.update_video_path(sub_id, video_path)
                logger.info(f"Demo video saved for submission {sub_id}")
            except Exception:
                logger.exception(f"Video recording failed for submission {sub_id} (non-fatal)")
```

- [ ] **Step 3: Verify the evaluator module imports cleanly**

```bash
cd scoreboard && python -c "from scoreboard import evaluator; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add scoreboard/scoreboard/evaluator.py
git commit -m "feat: record individual model demo video after evaluation"
```

---

## Task 4: API route to serve video + has_video in scoreboard

**Files:**
- Modify: `scoreboard/main.py`
- Test: `scoreboard/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

Open `scoreboard/tests/test_api.py` and add (check existing fixtures — typically uses `TestClient`):

```python
class TestVideoEndpoint:
    def test_video_not_found_when_no_video(self, client, submission_id):
        # submission_id fixture should create a submission with no video_path
        resp = client.get(f"/api/video/{submission_id}")
        assert resp.status_code == 404

    def test_video_not_found_for_unknown_id(self, client):
        resp = client.get("/api/video/99999")
        assert resp.status_code == 404

    def test_scoreboard_has_video_false_when_no_video(self, client, submission_id):
        resp = client.get("/api/scoreboard")
        assert resp.status_code == 200
        subs = resp.json()["submissions"]
        match = next((s for s in subs if s["id"] == submission_id), None)
        assert match is not None
        assert match["has_video"] is False
```

(Check `test_api.py` for the existing `client` and `submission_id` fixture patterns and replicate them.)

- [ ] **Step 2: Run to verify failure**

```bash
cd scoreboard && python -m pytest tests/test_api.py::TestVideoEndpoint -v
```

Expected: FAILED — endpoint doesn't exist yet.

- [ ] **Step 3: Add route and has_video to main.py**

In `main.py`, add import at top if not present:
```python
from fastapi.responses import FileResponse, JSONResponse, Response
```
(FileResponse is already imported — just keep it.)

Add new route after the `scoreboard()` route:
```python
@app.get("/api/video/{sub_id}")
async def get_video(sub_id: int):
    sub = db.get_submission(sub_id)
    if not sub or not sub.get("video_path"):
        raise HTTPException(404, "Відео не знайдено")
    path = Path(sub["video_path"])
    if not path.exists():
        raise HTTPException(404, "Файл відео не знайдено")
    return FileResponse(str(path), media_type="video/mp4")
```

In the `scoreboard()` route, inside the `for sub in active:` loop, add:
```python
        sub["has_video"] = bool(sub.get("video_path"))
```

- [ ] **Step 4: Run tests**

```bash
cd scoreboard && python -m pytest tests/test_api.py::TestVideoEndpoint -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add scoreboard/main.py scoreboard/tests/test_api.py
git commit -m "feat: add /api/video/{sub_id} route and has_video field in scoreboard API"
```

---

## Task 5: Frontend — modal HTML + CSS

**Files:**
- Modify: `scoreboard/static/index.html`
- Modify: `scoreboard/static/style.css`

- [ ] **Step 1: Add modal HTML to index.html**

Add before the closing `</body>` tag (before `<script>`):

```html
    <!-- Video modal -->
    <div id="video-modal" class="modal-overlay hidden" role="dialog" aria-modal="true">
        <div class="modal-box">
            <button id="modal-close" class="modal-close" aria-label="Закрити">&times;</button>
            <video id="modal-video" controls autoplay muted loop width="640" height="480"></video>
        </div>
    </div>
```

- [ ] **Step 2: Add modal CSS to style.css**

Append to the end of `style.css`:

```css
/* Video modal */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.modal-overlay.hidden { display: none; }

.modal-box {
    position: relative;
    background: #1a1a2e;
    border-radius: 8px;
    padding: 1rem;
    max-width: 95vw;
}

.modal-close {
    position: absolute;
    top: 0.4rem;
    right: 0.6rem;
    background: none;
    border: none;
    color: #ccc;
    font-size: 1.6rem;
    cursor: pointer;
    line-height: 1;
}
.modal-close:hover { color: #fff; }

.btn-video {
    background: #2a5298;
    color: #fff;
    border: none;
    border-radius: 4px;
    padding: 3px 10px;
    cursor: pointer;
    font-size: 0.82rem;
}
.btn-video:hover { background: #3a62b8; }
```

- [ ] **Step 3: Commit**

```bash
git add scoreboard/static/index.html scoreboard/static/style.css
git commit -m "feat: add video modal HTML and CSS"
```

---

## Task 6: Frontend — video button in table + modal logic

**Files:**
- Modify: `scoreboard/static/app.js`

- [ ] **Step 1: Add modal open/close logic**

At the bottom of `app.js`, add:

```javascript
function openVideoModal(subId) {
    const modal = $("video-modal");
    const video = $("modal-video");
    video.src = `${API}/api/video/${subId}`;
    modal.classList.remove("hidden");
    video.play().catch(() => {});
}

function closeVideoModal() {
    const modal = $("video-modal");
    const video = $("modal-video");
    modal.classList.add("hidden");
    video.pause();
    video.src = "";
}
```

In `document.addEventListener("DOMContentLoaded", ...)`, add:
```javascript
    $("modal-close").addEventListener("click", closeVideoModal);
    $("video-modal").addEventListener("click", (e) => {
        if (e.target === $("video-modal")) closeVideoModal();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeVideoModal();
    });
```

- [ ] **Step 2: Add "Відео" column to renderTable()**

In `renderTable()`, update the `<thead>` row to add a header:
```javascript
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
            <th>Відео</th>
        </tr></thead><tbody>`;
```

In the `sorted.forEach` loop, update the `html +=` row to add a final `<td>`:
```javascript
        const videoCell = s.has_video
            ? `<td><button class="btn-video" onclick="openVideoModal(${s.id})">&#9654; Переглянути</button></td>`
            : `<td>—</td>`;

        html += `<tr>
            <td>${rank}</td>
            <td>${escHtml(s.name)} ${escHtml(s.surname)}</td>
            <td>${escHtml(s.subgroup)}</td>
            <td class="${scoreClass(s.standard_mean)}">${stdScore}</td>
            <td class="${scoreClass(s.individual_mean)}">${indScore}</td>
            <td><strong>${rankScore}</strong></td>
            <td>${statusBadge}</td>
            <td>${dist}</td>
            ${videoCell}
        </tr>`;
```

- [ ] **Step 3: Commit**

```bash
git add scoreboard/static/app.js
git commit -m "feat: add video button to scoreboard table with modal player"
```

---

## Task 7: Coolify Deployment Instructions

This task produces no code — it's the setup guide for production.

### Persistent Volume

In Coolify, for the scoreboard service:

1. Go to **Storage** tab of the service.
2. Add a persistent volume:
   - **Source path (host):** leave blank (Coolify manages it) or set a named volume
   - **Mount path (container):** `/app/uploads`
3. Set environment variable: `UPLOADS_DIR=/app/uploads`

This ensures `uploads/` (and all generated MP4s) survive container redeploys.

### Verify it works

After deploying with the new code:
1. Submit a model via the UI.
2. Wait for `status = done`.
3. A `▶ Переглянути` button should appear in the row.
4. Click it — video should play in the modal.

Check logs for: `Demo video saved for submission {id}` or `Video recording failed` (non-fatal).

---

## Self-Review

**Spec coverage check:**
- ✅ Video generated during evaluation (Task 3)
- ✅ Individual model only (Task 3 uses `ind_params` and `model_individual_path`)
- ✅ Stored on local persistent volume (Task 3 writes to `UPLOADS_DIR/{sub_id}/`)
- ✅ Coolify setup instructions (Task 7)
- ✅ Button per row in scoreboard (Task 6)
- ✅ Modal video player (Tasks 5 + 6)
- ✅ Non-fatal failure — evaluation result is not lost if video recording fails (Task 3)
- ✅ Existing DB gets migration (Task 2)

**Placeholder scan:** None found.

**Type consistency:**
- `update_video_path(sub_id: int, video_path: str)` defined in Task 2, called in Task 3 — consistent.
- `has_video` set in `main.py` scoreboard route (Task 4), read in `app.js` as `s.has_video` (Task 6) — consistent.
- Modal element IDs: `video-modal`, `modal-close`, `modal-video` defined in Task 5, used in Task 6 — consistent.

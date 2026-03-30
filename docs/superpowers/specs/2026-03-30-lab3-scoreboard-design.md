# Lab 3 Scoreboard — Design Spec

## Overview

A self-hosted scoreboard web app for Lab #3 (LunarLander DQN). Students upload trained models via email PIN verification. Models are evaluated in a background process. Results are displayed on a public leaderboard grouped by subgroup.

Hosted locally on instructor's machine, exposed via Cloudflare tunnel.

## Architecture

```
Browser (vanilla JS)  <-->  FastAPI  <-->  SQLite
                                |
                                +--> Background evaluator (subprocess)
                                +--> Resend API (email)
```

Single Python process. FastAPI serves both the API and the static frontend. Background evaluation runs in a thread with a queue.

## Upload Flow

1. Student enters their `@lpnu.ua` email on the form.
2. `POST /api/request-pin` — server generates a 6-digit PIN, stores it with 15-min expiry, sends it via Resend.
3. Student receives PIN via email, fills the rest of the form:
   - PIN
   - Name, surname
   - Subgroup (dropdown from hard-coded list)
   - Hyperparameters JSON (DQN training params: learning_rate, buffer_size, batch_size, exploration_fraction, gamma, etc.)
   - `model_standard.zip` file
   - `model_individual.zip` file
4. `POST /api/upload` — server:
   - Validates PIN (exists, not expired, not used)
   - Validates email ends with `@lpnu.ua`
   - Validates subgroup is in the active subgroups list
   - Validates both files are present and are `.zip` files
   - Marks PIN as used
   - Saves files to `./uploads/<submission_id>/`
   - Computes hyperparameter min-distance (see below)
   - If same email already has a submission, the new one replaces it on the scoreboard (old row kept in DB but marked superseded; old files can be cleaned up)
   - Inserts submission with `status=pending`
5. Background evaluator picks up pending submissions sequentially.

## Scoreboard Flow

- `GET /api/scoreboard` returns all active submissions (latest per email, i.e. where `superseded_by IS NULL`) with scores.
- Server computes `rank_score` using the formula in `scoring.py`.
- Frontend groups by subgroup, sorts by rank_score descending, displays tables.
- No authentication required to view.

## Database Schema (SQLite)

### `pins`

| Column     | Type     | Notes                        |
|------------|----------|------------------------------|
| id         | INTEGER  | PRIMARY KEY                  |
| email      | TEXT     | must end with @lpnu.ua       |
| pin        | TEXT     | 6-digit string               |
| created_at | DATETIME | default now                  |
| expires_at | DATETIME | created_at + 15 minutes      |
| used       | BOOLEAN  | default FALSE                |

### `submissions`

| Column                | Type     | Notes                                    |
|-----------------------|----------|------------------------------------------|
| id                    | INTEGER  | PRIMARY KEY                              |
| email                 | TEXT     | NOT NULL                                 |
| name                  | TEXT     | NOT NULL                                 |
| surname               | TEXT     | NOT NULL                                 |
| subgroup              | TEXT     | NOT NULL                                 |
| param_a               | INTEGER  | NOT NULL, derived from student's name    |
| hyperparameters       | TEXT     | JSON string of DQN training params       |
| hyperparam_min_dist   | REAL     | min Euclidean distance to other entries   |
| model_standard_path   | TEXT     | path on disk                             |
| model_individual_path | TEXT     | path on disk                             |
| standard_mean         | REAL     | filled after evaluation                  |
| standard_std          | REAL     | filled after evaluation                  |
| individual_mean       | REAL     | filled after evaluation                  |
| individual_std        | REAL     | filled after evaluation                  |
| status                | TEXT     | pending / evaluating / done / error      |
| error_message         | TEXT     | nullable, set on evaluation failure      |
| superseded_by         | INTEGER  | nullable, FK to newer submission by same email |
| created_at            | DATETIME | default now                              |
| evaluated_at          | DATETIME | nullable, set when evaluation completes  |

### `config`

| Column | Type | Notes                                           |
|--------|------|-------------------------------------------------|
| key    | TEXT | PRIMARY KEY                                     |
| value  | TEXT | JSON string, e.g. key="subgroups", value=list   |

## Hyperparameter Distance

Purpose: detect students who copied each other's DQN training configuration.

- Student submits a JSON object with numeric DQN hyperparameters (e.g. `{"learning_rate": 0.001, "buffer_size": 50000, "batch_size": 64, "exploration_fraction": 0.1, "gamma": 0.99}`).
- On each new upload, for all active submissions:
  1. Extract the union of all hyperparameter keys across all submissions.
  2. For each submission, build a numeric vector (missing keys default to 0).
  3. Min-max normalize each dimension across the full dataset.
  4. Compute pairwise Euclidean distances.
  5. Store the minimum distance to any other submission in `hyperparam_min_dist`.
- This is recomputed for ALL active submissions on each new upload (O(n^2), trivial at n<=100).

## Background Evaluation

- A single background thread with a `queue.Queue`.
- On startup, any submissions with `status=pending` or `status=evaluating` are re-queued.
- The worker processes one submission at a time:
  1. Set `status=evaluating`
  2. Load `model_standard.zip` via `DQN.load()`
  3. Evaluate on standard LunarLander-v3 env (100 episodes) → `standard_mean`, `standard_std`
  4. Compute individual env params from `param_a` (using `compute_individual_params()` from existing code)
  5. Load `model_individual.zip`, evaluate on individual env (100 episodes) → `individual_mean`, `individual_std`
  6. On success: write scores, set `status=done`, set `evaluated_at`
  7. On failure: set `status=error`, write `error_message`
- Reuses evaluation logic from existing `leaderboard_runner.py`.

## Ranking Formula

Located in a single file `scoring.py` for easy editing:

```python
def compute_rank_score(submission: dict) -> float:
    """Edit this formula to change ranking."""
    standard = submission["standard_mean"] or 0
    individual = submission["individual_mean"] or 0
    return standard * 0.7 + individual * 0.3
```

Server computes and attaches `rank_score` to each submission in the API response.

## Email (Resend)

- Single env var: `RESEND_API_KEY`
- Sender: configured in `config.py` (must match verified domain/email in Resend)
- PIN email is plain text, contains the 6-digit code and a note that it expires in 15 minutes.
- Only `@lpnu.ua` emails are accepted.

## Frontend

Single HTML page served by FastAPI at `/`. No build step.

- **Upload section**: two-step form (email → PIN → full form with file uploads)
- **Scoreboard section**: tabs or sections per subgroup, table with columns: rank, name, surname, standard score, individual score, combined score, status, hyperparam distance
- Fetches data from `GET /api/scoreboard`
- Auto-refreshes or manual refresh button
- Vanilla JS (or Alpine.js if helpful). Minimal CSS.

## API Endpoints

| Method | Path              | Auth       | Description                        |
|--------|-------------------|------------|------------------------------------|
| GET    | /                 | none       | Serve index.html                   |
| POST   | /api/request-pin  | none       | Send PIN to @lpnu.ua email         |
| POST   | /api/upload       | PIN        | Upload submission                  |
| GET    | /api/scoreboard   | none       | Get all active submissions + scores|

## Configuration

`config.py` or `.env` file:

- `RESEND_API_KEY` — Resend API key
- `RESEND_FROM_EMAIL` — verified sender email
- `SUBGROUPS` — list of active subgroup names (editable; old subgroups still appear on scoreboard if they have submissions)
- `PIN_EXPIRY_MINUTES` — default 15
- `EVALUATION_EPISODES` — default 100
- `UPLOADS_DIR` — default `./uploads`
- `DATABASE_PATH` — default `./scoreboard.db`

## File Structure

```
scoreboard/
    main.py              # FastAPI app, route handlers
    db.py                # SQLite setup, queries
    scoring.py           # Ranking formula (edit here)
    evaluator.py         # Background evaluation worker
    config.py            # Settings, env vars, subgroup list
    email_service.py     # Resend integration
    hyperparams.py       # Distance calculation
    static/
        index.html       # Single-page frontend
        style.css
        app.js
    uploads/             # Model files stored here
    scoreboard.db        # SQLite database (created at startup)
```

## Constraints & Assumptions

- Max ~100 submissions total.
- Sequential evaluation is acceptable (one model at a time).
- Server has Python 3.10+, gymnasium, stable-baselines3 installed.
- Cloudflare tunnel handles HTTPS termination.
- No admin UI needed — instructor edits config/DB directly if needed.
- File size limit: reasonable cap (e.g. 50MB per .zip) to prevent abuse.

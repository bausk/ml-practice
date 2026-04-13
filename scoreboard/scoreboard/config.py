import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL: str = os.environ.get("RESEND_FROM_EMAIL", "noreply@example.com")

DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/scoreboard")
UPLOADS_DIR: Path = Path(os.environ.get("UPLOADS_DIR", "./uploads"))

PIN_EXPIRY_MINUTES: int = int(os.environ.get("PIN_EXPIRY_MINUTES", "15"))
EVALUATION_EPISODES: int = int(os.environ.get("EVALUATION_EPISODES", "100"))

MAX_FILE_SIZE_MB: int = 50

# Editable list of active subgroups.
# Students can only select from this list for new uploads.
# Old subgroups with existing submissions still appear on the scoreboard.
SUBGROUPS: list[str] = [
    "ПЗ-33-1",
    "ПЗ-33-2",
    "ПЗ-34-1",
    "ПЗ-34-2",
    "ПЗ-35-1",
    "ПЗ-35-2",
    "Викладачі/Інше"
]

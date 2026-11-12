from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR}/music.db"
)

# Local music storage inside the Docker container
MUSIC_DIR = Path(
    os.getenv("MUSIC_DIR", str(BASE_DIR / "music_library"))
)



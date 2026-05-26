from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'cadver.db'}"
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".dwg", ".dxf"}

import hashlib
import shutil
from pathlib import Path
from app.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS


def validate_file(filename: str, content: bytes) -> str | None:
    """返回错误信息，None 表示通过"""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"不支持的文件格式 {ext}，仅允许 {', '.join(ALLOWED_EXTENSIONS)}"
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        return f"文件超过 {MAX_FILE_SIZE_MB}MB 限制"
    return None


def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_file(project_id: int, series_id: int, version_number: int,
              filename: str, content: bytes) -> str:
    """存储文件，返回相对路径"""
    rel = f"projects/{project_id}/{series_id}/v{version_number}"
    dir_path = UPLOAD_DIR / rel
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    file_path.write_bytes(content)
    return str(rel / filename)

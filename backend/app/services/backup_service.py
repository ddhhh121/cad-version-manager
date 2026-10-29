import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from app.config import BASE_DIR, UPLOAD_DIR

BACKUP_DIR = BASE_DIR / "backups"


def ensure_backup_dir():
    """确保备份目录存在"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup() -> dict:
    """创建备份"""
    ensure_backup_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = BACKUP_DIR / f"{backup_name}.zip"

    # 创建 zip 文件
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加数据库文件
        db_path = BASE_DIR / "cadver.db"
        if db_path.exists():
            zipf.write(db_path, "cadver.db")

        # 添加 uploads 目录
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(BASE_DIR)
                    zipf.write(file_path, arcname)

    # 获取文件大小
    file_size = backup_path.stat().st_size

    return {
        "id": backup_name,
        "name": backup_name,
        "size": file_size,
        "created_at": datetime.now().isoformat(),
    }


def list_backups() -> list[dict]:
    """列出所有备份"""
    ensure_backup_dir()

    backups = []
    for file_path in sorted(BACKUP_DIR.glob("backup_*.zip"), reverse=True):
        stat = file_path.stat()
        backups.append({
            "id": file_path.stem,
            "name": file_path.stem,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })

    return backups


def get_backup_path(backup_id: str) -> Path | None:
    """获取备份文件路径"""
    ensure_backup_dir()

    backup_path = BACKUP_DIR / f"{backup_id}.zip"
    if backup_path.exists():
        return backup_path
    return None


def restore_backup(zip_path: str) -> dict:
    """从备份恢复"""
    backup_dir = BASE_DIR / "temp_restore"
    backup_dir.mkdir(exist_ok=True)

    try:
        # 解压备份
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(backup_dir)

        # 恢复数据库
        db_backup = backup_dir / "cadver.db"
        if db_backup.exists():
            db_target = BASE_DIR / "cadver.db"
            shutil.copy2(db_backup, db_target)

        # 恢复 uploads 目录
        uploads_backup = backup_dir / "uploads"
        if uploads_backup.exists():
            if UPLOAD_DIR.exists():
                shutil.rmtree(UPLOAD_DIR)
            shutil.copytree(uploads_backup, UPLOAD_DIR)

        return {"status": "ok", "message": "恢复成功"}

    finally:
        # 清理临时目录
        if backup_dir.exists():
            shutil.rmtree(backup_dir)


def delete_backup(backup_id: str) -> bool:
    """删除备份"""
    backup_path = get_backup_path(backup_id)
    if backup_path:
        backup_path.unlink()
        return True
    return False

import subprocess
import shutil
from pathlib import Path
from app.config import UPLOAD_DIR


def generate_thumbnail(file_path: str) -> str | None:
    """生成缩略图 PNG，返回缩略图相对路径，失败返回 None"""
    src = Path(file_path)
    thumb_filename = src.stem + "_thumb.png"
    thumb_dir = src.parent
    thumb_path = thumb_dir / thumb_filename

    # 尝试 ODA File Converter
    if _try_oda_converter(src, thumb_path):
        return str(thumb_path.relative_to(UPLOAD_DIR))

    # 尝试 LibreCAD
    if _try_librecad(src, thumb_path):
        return str(thumb_path.relative_to(UPLOAD_DIR))

    # 兜底：生成 SVG 占位图
    _generate_placeholder(thumb_path)
    return str(thumb_path.relative_to(UPLOAD_DIR))


def _try_oda_converter(src: Path, dst: Path) -> bool:
    oda_paths = [
        "ODAFileConverter",
        "ODAFileConverter.exe",
    ]
    for cmd in oda_paths:
        if shutil.which(cmd) is None:
            continue
        try:
            subprocess.run(
                [cmd, str(src), str(dst.parent), "PNG"],
                timeout=60,
                capture_output=True,
            )
            return dst.exists()
        except Exception:
            pass
    return False


def _try_librecad(src: Path, dst: Path) -> bool:
    if shutil.which("LibreCAD") is None:
        return False
    try:
        subprocess.run(
            ["LibreCAD", "--export", str(src), "--format", "png",
             "--output", str(dst)],
            timeout=60,
            capture_output=True,
        )
        return dst.exists()
    except Exception:
        return False


def _generate_placeholder(path: Path) -> None:
    """生成一个 SVG 占位缩略图"""
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
        '<rect width="400" height="300" fill="#f0f0f0"/>'
        '<text x="200" y="150" text-anchor="middle" '
        'font-family="sans-serif" font-size="16" fill="#999">'
        '缩略图不可用</text></svg>'
    )
    path.write_text(svg_content)

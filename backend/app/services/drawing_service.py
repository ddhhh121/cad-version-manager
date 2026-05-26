import re
from pathlib import Path

DRAWING_NUMBER_PATTERN = re.compile(
    r"(?:^|[_\-\s])"
    r"(A[0-4oO][a-zA-Z]*|a[0-4oO][a-zA-Z]*)"
    r"[_\-\s]*"
    r"([\w一-鿿]+?)"
    r"(?:[_\-\s]*(?:模型|图纸|bak|副本|copy))?"
    r"(?:\.[dD][wW][gG]|\.[dD][xX][fF])?$"
)


def extract_drawing_number(filename: str) -> str:
    """从文件名提取图号，如 'a2v带轮.dwg' → 'A2V带轮'"""
    name = Path(filename).stem
    # 移除 .bak 后缀
    if name.lower().endswith(".bak"):
        name = name[:-4]

    m = DRAWING_NUMBER_PATTERN.search(name)
    if m:
        paper_size = m.group(1).upper()
        part_name = m.group(2)
        return f"{paper_size}{part_name}"

    # 兜底：直接用文件名（去扩展名）
    return name


def extract_metadata_from_dxf(file_path: str) -> dict:
    """从 DXF 文件提取标题栏信息，失败返回空 dict"""
    try:
        import ezdxf
        doc = ezdxf.readfile(file_path)
    except Exception:
        return {}

    result = {}
    try:
        for entity in doc.modelspace():
            if entity.dxftype() == "MTEXT":
                text = entity.plain_text().strip()
                for key in ["图号", "名称", "材料", "数量", "比例", "设计"]:
                    if text.startswith(key):
                        result[key] = text[len(key):].lstrip(":：").strip()
    except Exception:
        pass
    return result

# CAD 图纸版本管理器 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Web 应用，让机械工程师管理 DWG/DXF 图纸文件的版本，追踪变更，快速找到最新版。

**Architecture:** FastAPI 后端提供 REST API + SQLite 存储元数据 + 本地文件系统存储图纸。Vue 3 前端 SPA 提供 4 个核心页面。不解析 DWG 内容，改用文件哈希 + DXF 元数据 + 缩略图方案。

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, SQLite, ezdxf, Vue 3, Vite, pytest, httpx

---

## 文件结构

```
D:/CAD管理模块/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── projects.py
│   │   │   ├── series.py
│   │   │   └── versions.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── file_service.py
│   │       ├── drawing_service.py
│   │       └── thumbnail_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_projects.py
│   │   ├── test_upload.py
│   │   ├── test_series.py
│   │   ├── test_versions.py
│   │   └── test_drawing_service.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/index.js
│   │   ├── api/index.js
│   │   ├── views/
│   │   │   ├── ProjectList.vue
│   │   │   ├── ProjectDetail.vue
│   │   │   └── VersionCompare.vue
│   │   └── components/
│   │       ├── ProjectCard.vue
│   │       ├── DrawingSeriesList.vue
│   │       ├── VersionTimeline.vue
│   │       ├── OldVersionWarning.vue
│   │       ├── VersionCompareCards.vue
│   │       └── DiffTable.vue
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .gitignore
└── uploads/   (runtime, gitignored)
```

---

### Task 1: 后端项目骨架 + 依赖

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`
- Create: `backend/app/database.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/app/routes/__init__.py`
- Create: `backend/app/services/__init__.py`
- Modify: `.gitignore`

- [ ] **Step 1: 创建 .gitignore**

```
uploads/
__pycache__/
*.pyc
.env
node_modules/
dist/
*.db
```

- [ ] **Step 2: 创建 requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
python-multipart==0.0.18
ezdxf==1.3.5
httpx==0.28.1
pytest==8.3.4
```

- [ ] **Step 3: 创建 config.py**

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'cadver.db'}"
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".dwg", ".dxf"}
```

- [ ] **Step 4: 创建 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: 创建 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import projects, series, versions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CAD Version Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(series.router, prefix="/api")
app.include_router(versions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: 创建空 __init__.py 文件**

```python
# backend/app/__init__.py
```

```python
# backend/app/routes/__init__.py
```

```python
# backend/app/services/__init__.py
```

```python
# backend/tests/__init__.py
```

- [ ] **Step 7: 创建 conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import BASE_DIR

TEST_DB_URL = f"sqlite:///{BASE_DIR / 'test.db'}"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
```

- [ ] **Step 8: 安装依赖并验证**

```bash
cd D:/CAD管理模块/backend && pip install -r requirements.txt
```

- [ ] **Step 9: 启动并验证 health endpoint**

```bash
cd D:/CAD管理模块/backend && uvicorn app.main:app --reload &
sleep 3
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 10: 运行空测试确认框架正常**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/ -v
```

Expected: no tests collected (but no errors)

- [ ] **Step 11: Commit**

```bash
cd D:/CAD管理模块 && git add .gitignore backend/
git commit -m "feat: backend project skeleton with FastAPI + SQLAlchemy + pytest"
```

---

### Task 2: 数据模型

**Files:**
- Create: `backend/app/models.py`

- [ ] **Step 1: 编写 models.py**

```python
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    series_list = relationship(
        "DrawingSeries", back_populates="project", cascade="all, delete-orphan"
    )


class DrawingSeries(Base):
    __tablename__ = "drawing_series"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    drawing_number = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    project = relationship("Project", back_populates="series_list")
    versions = relationship(
        "DrawingVersion", back_populates="series",
        order_by="DrawingVersion.version_number.desc()",
        cascade="all, delete-orphan",
    )


class DrawingVersion(Base):
    __tablename__ = "drawing_versions"
    __table_args__ = (
        UniqueConstraint("series_id", "file_hash", name="uq_series_hash"),
    )

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("drawing_series.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    filename = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    thumbnail_path = Column(String(1000), nullable=True)
    metadata_json = Column(JSON, default=dict)
    change_note = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    series = relationship("DrawingSeries", back_populates="versions")
```

- [ ] **Step 2: 验证模型可创建**

```bash
cd D:/CAD管理模块/backend && python -c "
from app.database import engine, Base
from app.models import Project, DrawingSeries, DrawingVersion
Base.metadata.create_all(bind=engine)
print('Tables created successfully')
"
```

Expected: `Tables created successfully`

- [ ] **Step 3: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/models.py
git commit -m "feat: add SQLAlchemy models for Project, DrawingSeries, DrawingVersion"
```

---

### Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas.py`

- [ ] **Step 1: 编写 schemas.py**

```python
from datetime import datetime
from pydantic import BaseModel, Field


# ── Project ──

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    series_count: int = 0

    model_config = {"from_attributes": True}


# ── DrawingSeries ──

class DrawingSeriesOut(BaseModel):
    id: int
    project_id: int
    drawing_number: str
    created_at: datetime
    latest_version: "DrawingVersionOut | None" = None
    version_count: int = 0

    model_config = {"from_attributes": True}


# ── DrawingVersion ──

class DrawingVersionOut(BaseModel):
    id: int
    series_id: int
    version_number: int
    filename: str
    file_hash: str
    file_size: int
    thumbnail_path: str | None = None
    metadata_json: dict = {}
    change_note: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangeNoteUpdate(BaseModel):
    change_note: str


# ── Upload response ──

class UploadResult(BaseModel):
    series_id: int
    version_id: int
    version_number: int
    drawing_number: str
    is_new_series: bool
    filename: str
    file_size: int


# ── Compare ──

class FieldDiff(BaseModel):
    field: str
    label: str
    old_value: str
    new_value: str
    changed: bool


class CompareResult(BaseModel):
    version_new: DrawingVersionOut
    version_old: DrawingVersionOut
    hash_match: bool
    size_diff_percent: float
    diffs: list[FieldDiff]
```

- [ ] **Step 2: 验证 schemas 可导入**

```bash
cd D:/CAD管理模块/backend && python -c "from app.schemas import ProjectCreate, UploadResult, CompareResult; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/schemas.py
git commit -m "feat: add Pydantic schemas for all API inputs and outputs"
```

---

### Task 4: 文件服务（哈希 + 存储 + 图号提取）

**Files:**
- Create: `backend/app/services/file_service.py`
- Create: `backend/app/services/drawing_service.py`
- Create: `backend/tests/test_drawing_service.py`

- [ ] **Step 1: 编写 file_service.py**

```python
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
```

- [ ] **Step 2: 编写 drawing_service.py**

```python
import re
from pathlib import Path

DRAWING_NUMBER_PATTERN = re.compile(
    r"(?:^|[_\-\s])"
    r"(A[0-4]|a[0-4])"
    r"[_\-\s]*"
    r"([一-鿿\w]+?)"
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
```

- [ ] **Step 3: 编写 test_drawing_service.py**

```python
from app.services.drawing_service import extract_drawing_number


def test_extract_standard_pattern():
    assert extract_drawing_number("a2v带轮.dwg") == "A2V带轮"


def test_extract_with_underscore():
    assert extract_drawing_number("A3_动刀刃.bak") == "A3动刀刃"


def test_extract_with_space():
    assert extract_drawing_number("a4 轴承座.dwg") == "A4轴承座"


def test_extract_fallback():
    result = extract_drawing_number("unknown_file.dwg")
    assert result == "unknown_file"


def test_extract_assembly_drawing():
    assert extract_drawing_number("ao卧式钢筋切断机装配图.dwg") == "AO卧式钢筋切断机装配图"


def test_extract_with_model_suffix():
    assert extract_drawing_number("A3动刀刃-模型.pdf") == "A3动刀刃"
```

- [ ] **Step 4: 运行测试**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/test_drawing_service.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/services/ backend/tests/test_drawing_service.py
git commit -m "feat: add file service, drawing number extraction, and tests"
```

---

### Task 5: 缩略图服务

**Files:**
- Create: `backend/app/services/thumbnail_service.py`

- [ ] **Step 1: 编写 thumbnail_service.py**

```python
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

    # 兜底：复制一个占位文件
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
```

- [ ] **Step 2: 验证导入**

```bash
cd D:/CAD管理模块/backend && python -c "from app.services.thumbnail_service import generate_thumbnail; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/services/thumbnail_service.py
git commit -m "feat: add thumbnail generation service with fallback placeholder"
```

---

### Task 6: Projects API

**Files:**
- Create: `backend/app/routes/projects.py`
- Create: `backend/tests/test_projects.py`

- [ ] **Step 1: 编写 projects.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectOut

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        result.append(ProjectOut(
            id=p.id,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            series_count=len(p.series_list),
        ))
    return result


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=body.name, description=body.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        series_count=0,
    )


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        series_count=len(project.series_list),
    )
```

- [ ] **Step 2: 编写 test_projects.py**

```python
def test_create_project(client):
    resp = client.post("/api/projects", json={"name": "测试项目", "description": "测试"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "测试项目"
    assert data["series_count"] == 0
    assert "id" in data


def test_list_projects(client):
    client.post("/api/projects", json={"name": "项目A"})
    client.post("/api/projects", json={"name": "项目B"})
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "项目B"  # 最新在前


def test_get_project(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "测试"


def test_get_project_404(client):
    resp = client.get("/api/projects/999")
    assert resp.status_code == 404
```

- [ ] **Step 3: 运行测试**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/test_projects.py -v
```

Expected: 4 passed

- [ ] **Step 4: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/routes/projects.py backend/tests/test_projects.py
git commit -m "feat: add projects CRUD API with tests"
```

---

### Task 7: 上传 API（核心逻辑）

**Files:**
- Create: `backend/app/routes/upload.py` → 合并到 `backend/app/routes/projects.py`
- Create: `backend/tests/test_upload.py`

实际上传逻辑放在 projects router 中作为子路径。

- [ ] **Step 1: 在 projects.py 中添加上传端点**

在 `backend/app/routes/projects.py` 末尾追加：

```python
from fastapi import UploadFile, File, HTTPException
from app.services.file_service import validate_file, compute_hash, save_file
from app.services.drawing_service import extract_drawing_number, extract_metadata_from_dxf
from app.services.thumbnail_service import generate_thumbnail
from app.models import DrawingSeries, DrawingVersion
from app.schemas import UploadResult


@router.post("/projects/{project_id}/upload", response_model=UploadResult)
def upload_drawing(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    content = file.file.read()
    err = validate_file(file.filename, content)
    if err:
        raise HTTPException(status_code=400, detail=err)

    file_hash = compute_hash(content)
    drawing_number = extract_drawing_number(file.filename)

    # 查找或创建 DrawingSeries
    series = (
        db.query(DrawingSeries)
        .filter(
            DrawingSeries.project_id == project_id,
            DrawingSeries.drawing_number == drawing_number,
        )
        .first()
    )
    is_new_series = series is None

    if is_new_series:
        series = DrawingSeries(project_id=project_id, drawing_number=drawing_number)
        db.add(series)
        db.flush()
    else:
        # 检查 hash 重复
        dup = (
            db.query(DrawingVersion)
            .filter(
                DrawingVersion.series_id == series.id,
                DrawingVersion.file_hash == file_hash,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=409,
                detail=f"此版本已存在：{drawing_number} v{dup.version_number}",
            )

    # 计算版本号
    max_v = (
        db.query(DrawingVersion.version_number)
        .filter(DrawingVersion.series_id == series.id)
        .order_by(DrawingVersion.version_number.desc())
        .first()
    )
    version_number = (max_v[0] + 1) if max_v else 1

    # 存储文件
    file_path = save_file(project_id, series.id, version_number, file.filename, content)

    # 缩略图
    thumb_path = generate_thumbnail(str(UPLOAD_DIR / file_path))

    # DXF 元数据
    metadata = {}
    if file.filename.lower().endswith(".dxf"):
        metadata = extract_metadata_from_dxf(str(UPLOAD_DIR / file_path))

    version = DrawingVersion(
        series_id=series.id,
        version_number=version_number,
        filename=file.filename,
        file_hash=file_hash,
        file_path=file_path,
        file_size=len(content),
        thumbnail_path=thumb_path,
        metadata_json=metadata,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    return UploadResult(
        series_id=series.id,
        version_id=version.id,
        version_number=version.version_number,
        drawing_number=drawing_number,
        is_new_series=is_new_series,
        filename=file.filename,
        file_size=len(content),
    )
```

- [ ] **Step 2: 编写 test_upload.py**

```python
import io


def test_upload_new_dxf_creates_series_and_version(client):
    # 先创建项目
    resp = client.post("/api/projects", json={"name": "测试项目"})
    pid = resp.json()["id"]

    content = (
        b"0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n"
    )
    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["drawing_number"] == "A3动刀刃"
    assert data["version_number"] == 1
    assert data["is_new_series"] is True
    assert "series_id" in data


def test_upload_duplicate_hash_rejected(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    content = b"test dwg content"
    # 第一次
    client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("a4齿轮.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    # 第二次，相同内容
    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("a4齿轮_v2.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    assert resp.status_code == 409


def test_upload_same_series_increments_version(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    resp1 = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃.dxf", io.BytesIO(b"v1 content"), "application/octet-stream")},
    )
    assert resp1.json()["version_number"] == 1

    resp2 = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃_修改.dxf", io.BytesIO(b"v2 content"), "application/octet-stream")},
    )
    assert resp2.json()["version_number"] == 2
    assert resp2.json()["is_new_series"] is False
    assert resp2.json()["series_id"] == resp1.json()["series_id"]


def test_upload_reject_non_dwg_dxf(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("readme.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_project_404(client):
    resp = client.post(
        "/api/projects/999/upload",
        files={"file": ("test.dxf", io.BytesIO(b"x"), "application/octet-stream")},
    )
    assert resp.status_code == 404
```

- [ ] **Step 3: 运行测试**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/test_upload.py -v
```

Expected: 5 passed

- [ ] **Step 4: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/routes/projects.py backend/tests/test_upload.py
git commit -m "feat: add upload endpoint with version chain logic and tests"
```

---

### Task 8: DrawingSeries + Version 查询 API

**Files:**
- Create: `backend/app/routes/series.py`
- Create: `backend/app/routes/versions.py`
- Create: `backend/tests/test_series.py`
- Create: `backend/tests/test_versions.py`

- [ ] **Step 1: 编写 series.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DrawingSeries, DrawingVersion, Project
from app.schemas import DrawingSeriesOut, DrawingVersionOut

router = APIRouter(tags=["series"])


def _version_to_out(v: DrawingVersion) -> DrawingVersionOut:
    return DrawingVersionOut(
        id=v.id,
        series_id=v.series_id,
        version_number=v.version_number,
        filename=v.filename,
        file_hash=v.file_hash,
        file_size=v.file_size,
        thumbnail_path=v.thumbnail_path,
        metadata_json=v.metadata_json or {},
        change_note=v.change_note or "",
        created_at=v.created_at,
    )


@router.get("/series/{series_id}", response_model=DrawingSeriesOut)
def get_series(series_id: int, db: Session = Depends(get_db)):
    series = db.query(DrawingSeries).filter(DrawingSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="图纸系列不存在")
    versions = series.versions
    latest = _version_to_out(versions[0]) if versions else None
    return DrawingSeriesOut(
        id=series.id,
        project_id=series.project_id,
        drawing_number=series.drawing_number,
        created_at=series.created_at,
        latest_version=latest,
        version_count=len(versions),
    )


@router.get("/series/{series_id}/versions", response_model=list[DrawingVersionOut])
def list_versions(series_id: int, db: Session = Depends(get_db)):
    series = db.query(DrawingSeries).filter(DrawingSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="图纸系列不存在")
    return [_version_to_out(v) for v in series.versions]
```

- [ ] **Step 2: 编写 versions.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DrawingVersion
from app.schemas import DrawingVersionOut, ChangeNoteUpdate, CompareResult, FieldDiff
from app.config import UPLOAD_DIR

router = APIRouter(tags=["versions"])


def _version_to_out(v: DrawingVersion) -> DrawingVersionOut:
    return DrawingVersionOut(
        id=v.id,
        series_id=v.series_id,
        version_number=v.version_number,
        filename=v.filename,
        file_hash=v.file_hash,
        file_size=v.file_size,
        thumbnail_path=v.thumbnail_path,
        metadata_json=v.metadata_json or {},
        change_note=v.change_note or "",
        created_at=v.created_at,
    )


@router.get("/versions/{version_id}", response_model=DrawingVersionOut)
def get_version(version_id: int, db: Session = Depends(get_db)):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    return _version_to_out(v)


@router.post("/series/{series_id}/versions/{version_id}/note")
def update_change_note(
    series_id: int,
    version_id: int,
    body: ChangeNoteUpdate,
    db: Session = Depends(get_db),
):
    v = (
        db.query(DrawingVersion)
        .filter(
            DrawingVersion.id == version_id,
            DrawingVersion.series_id == series_id,
        )
        .first()
    )
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    v.change_note = body.change_note
    db.commit()
    return {"status": "ok"}


@router.get("/compare/{vid1}/{vid2}", response_model=CompareResult)
def compare_versions(vid1: int, vid2: int, db: Session = Depends(get_db)):
    """对比两个版本，vid1 通常为旧版 id，vid2 为新版 id"""
    v_old = db.query(DrawingVersion).filter(DrawingVersion.id == vid1).first()
    v_new = db.query(DrawingVersion).filter(DrawingVersion.id == vid2).first()
    if not v_old or not v_new:
        raise HTTPException(status_code=404, detail="版本不存在")

    if v_old.series_id != v_new.series_id:
        raise HTTPException(status_code=400, detail="只能对比同一图纸系列的版本")

    old_meta = v_old.metadata_json or {}
    new_meta = v_new.metadata_json or {}

    all_keys = set(old_meta.keys()) | set(new_meta.keys())
    diffs = []
    for key in sorted(all_keys):
        ov = str(old_meta.get(key, ""))
        nv = str(new_meta.get(key, ""))
        diffs.append(FieldDiff(
            field=key,
            label=key,
            old_value=ov,
            new_value=nv,
            changed=ov != nv,
        ))

    # 基础字段 diff
    diffs.insert(0, FieldDiff(
        field="file_size", label="文件大小",
        old_value=str(v_old.file_size),
        new_value=str(v_new.file_size),
        changed=v_old.file_size != v_new.file_size,
    ))
    diffs.insert(0, FieldDiff(
        field="file_hash", label="SHA256",
        old_value=v_old.file_hash[:16] + "...",
        new_value=v_new.file_hash[:16] + "...",
        changed=v_old.file_hash != v_new.file_hash,
    ))

    size_diff = 0.0
    if v_old.file_size > 0:
        size_diff = (v_new.file_size - v_old.file_size) / v_old.file_size * 100

    return CompareResult(
        version_new=_version_to_out(v_new),
        version_old=_version_to_out(v_old),
        hash_match=v_old.file_hash == v_new.file_hash,
        size_diff_percent=round(size_diff, 1),
        diffs=diffs,
    )


@router.get("/versions/{version_id}/thumbnail")
def get_thumbnail(version_id: int, db: Session = Depends(get_db)):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v or not v.thumbnail_path:
        raise HTTPException(status_code=404, detail="缩略图不存在")
    return FileResponse(UPLOAD_DIR / v.thumbnail_path)


@router.get("/versions/{version_id}/download")
def download_version(version_id: int, db: Session = Depends(get_db)):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    full_path = UPLOAD_DIR / v.file_path
    return FileResponse(full_path, filename=v.filename)
```

- [ ] **Step 3: 编写 test_series.py**

```python
import io


def _upload(client, pid, filename, content):
    return client.post(
        f"/api/projects/{pid}/upload",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
    )


def test_get_series_with_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    _upload(client, pid, "a4齿轮.dxf", b"v1")
    _upload(client, pid, "a4齿轮_v2.dxf", b"v2")

    # 从 project detail 拿到 series id
    presp = client.get(f"/api/projects/{pid}")
    # 需要 series 列表——等一下，project detail 还没有返回 series 列表
    # 所以直接从 series API 拿

    # 先拿到 upload 返回的 series_id
    up = _upload(client, pid, "A3连杆.dxf", b"test")
    sid = up.json()["series_id"]

    resp = client.get(f"/api/series/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["drawing_number"] == "A3连杆"
    assert data["version_count"] >= 1
    assert data["latest_version"] is not None


def test_list_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"v1")
    sid = up.json()["series_id"]

    resp = client.get(f"/api/series/{sid}/versions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["version_number"] >= 1


def test_series_404(client):
    resp = client.get("/api/series/999")
    assert resp.status_code == 404
```

- [ ] **Step 4: 编写 test_versions.py**

```python
import io


def _upload(client, pid, filename, content):
    return client.post(
        f"/api/projects/{pid}/upload",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
    )


def test_get_version(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"test content")
    vid = up.json()["version_id"]

    resp = client.get(f"/api/versions/{vid}")
    assert resp.status_code == 200
    assert resp.json()["filename"] == "a4齿轮.dxf"


def test_update_change_note(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"test")
    sid = up.json()["series_id"]
    vid = up.json()["version_id"]

    resp = client.post(
        f"/api/series/{sid}/versions/{vid}/note",
        json={"change_note": "改了齿数"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/versions/{vid}")
    assert resp.json()["change_note"] == "改了齿数"


def test_compare_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    v1 = _upload(client, pid, "A3动刀刃.dxf", b"v1 content")
    v2 = _upload(client, pid, "A3动刀刃_v2.dxf", b"v2 content different")

    vid1 = v1.json()["version_id"]
    vid2 = v2.json()["version_id"]

    resp = client.get(f"/api/compare/{vid1}/{vid2}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hash_match"] is False
    assert len(data["diffs"]) >= 2
    # SHA256 diff 应该是 changed=True
    sha_diff = [d for d in data["diffs"] if d["field"] == "file_hash"][0]
    assert sha_diff["changed"] is True


def test_compare_cross_series_rejected(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    v1 = _upload(client, pid, "A3动刀刃.dxf", b"a")
    v2 = _upload(client, pid, "a4齿轮.dxf", b"b")

    resp = client.get(
        f"/api/compare/{v1.json()['version_id']}/{v2.json()['version_id']}"
    )
    assert resp.status_code == 400
```

- [ ] **Step 5: 运行测试**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/test_series.py tests/test_versions.py -v
```

Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
cd D:/CAD管理模块 && git add backend/app/routes/series.py backend/app/routes/versions.py backend/tests/test_series.py backend/tests/test_versions.py
git commit -m "feat: add series, version, and compare APIs with tests"
```

---

### Task 9: 前端脚手架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "cad-version-manager",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^6.0.5"
  }
}
```

- [ ] **Step 2: 创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CAD 图纸版本管理器</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 main.js**

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'

createApp(App).use(router).mount('#app')
```

- [ ] **Step 5: 创建 App.vue**

```vue
<template>
  <div id="app-container">
    <header class="app-header">
      <router-link to="/" class="logo">CAD 版本管理器</router-link>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; }
.app-header { background: #1a1a2e; padding: 16px 32px; }
.app-header .logo { color: #fff; font-size: 18px; font-weight: 700; text-decoration: none; }
.app-main { max-width: 1200px; margin: 24px auto; padding: 0 16px; }
</style>
```

- [ ] **Step 6: 创建 router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'ProjectList', component: () => import('../views/ProjectList.vue') },
  { path: '/project/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetail.vue') },
  { path: '/compare/:vid1/:vid2', name: 'VersionCompare', component: () => import('../views/VersionCompare.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
```

- [ ] **Step 7: 创建 api/index.js**

```javascript
const BASE = '/api'

async function request(method, path, body) {
  const opts = { method, headers: {} }
  if (body && body instanceof FormData) {
    opts.body = body
  } else if (body) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return res.json()
}

export const api = {
  // Projects
  listProjects: () => request('GET', '/projects'),
  createProject: (data) => request('POST', '/projects', data),
  getProject: (id) => request('GET', `/projects/${id}`),
  uploadDrawing: (projectId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request('POST', `/projects/${projectId}/upload`, fd)
  },

  // Series
  getSeries: (id) => request('GET', `/series/${id}`),
  listVersions: (seriesId) => request('GET', `/series/${seriesId}/versions`),

  // Versions
  getVersion: (id) => request('GET', `/versions/${id}`),
  updateChangeNote: (seriesId, versionId, changeNote) =>
    request('POST', `/series/${seriesId}/versions/${versionId}/note`, { change_note: changeNote }),
  compareVersions: (vid1, vid2) => request('GET', `/compare/${vid1}/${vid2}`),
  getThumbnailUrl: (versionId) => `${BASE}/versions/${versionId}/thumbnail`,
  getDownloadUrl: (versionId) => `${BASE}/versions/${versionId}/download`,
}
```

- [ ] **Step 8: 安装依赖**

```bash
cd D:/CAD管理模块/frontend && npm install
```

- [ ] **Step 9: Commit**

```bash
cd D:/CAD管理模块 && git add frontend/
git commit -m "feat: scaffold Vue 3 frontend with router and API client"
```

---

### Task 10: 项目列表页 + ProjectCard

**Files:**
- Create: `frontend/src/views/ProjectList.vue`
- Create: `frontend/src/components/ProjectCard.vue`

- [ ] **Step 1: 创建 ProjectCard.vue**

```vue
<template>
  <div class="project-card" @click="$router.push(`/project/${project.id}`)">
    <h3>{{ project.name }}</h3>
    <p class="desc">{{ project.description || '暂无描述' }}</p>
    <div class="meta">
      <span>{{ project.series_count }} 个图纸系列</span>
      <span>{{ formatDate(project.created_at) }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ project: Object })
function formatDate(d) {
  return new Date(d).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.project-card {
  background: #fff; border-radius: 8px; padding: 20px;
  cursor: pointer; transition: box-shadow .2s;
  border: 1px solid #e8e8e8;
}
.project-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1); }
.project-card h3 { font-size: 18px; margin-bottom: 8px; }
.project-card .desc { color: #666; font-size: 14px; margin-bottom: 12px; }
.project-card .meta { display: flex; justify-content: space-between; color: #999; font-size: 13px; }
</style>
```

- [ ] **Step 2: 创建 ProjectList.vue**

```vue
<template>
  <div>
    <div class="page-header">
      <h1>项目</h1>
      <button class="btn-primary" @click="showCreate = true">+ 新建项目</button>
    </div>

    <div v-if="showCreate" class="create-form">
      <input v-model="newName" placeholder="项目名称" @keyup.enter="create" />
      <input v-model="newDesc" placeholder="描述（可选）" />
      <button class="btn-primary" @click="create">创建</button>
      <button class="btn-ghost" @click="showCreate = false">取消</button>
    </div>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="card-grid">
      <ProjectCard v-for="p in projects" :key="p.id" :project="p" />
      <div v-if="projects.length === 0" class="empty">还没有项目，新建一个吧</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api/index.js'
import ProjectCard from '../components/ProjectCard.vue'

const projects = ref([])
const loading = ref(true)
const error = ref('')
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try { projects.value = await api.listProjects() }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function create() {
  if (!newName.value.trim()) return
  await api.createProject({ name: newName.value.trim(), description: newDesc.value.trim() })
  showCreate.value = false
  newName.value = ''
  newDesc.value = ''
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h1 { font-size: 24px; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-left: 8px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.create-form { background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.create-form input { flex: 1; min-width: 140px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.empty { color: #999; text-align: center; padding: 60px; }
.error { color: #e74c3c; padding: 16px; }
</style>
```

- [ ] **Step 3: Commit**

```bash
cd D:/CAD管理模块 && git add frontend/src/views/ProjectList.vue frontend/src/components/ProjectCard.vue
git commit -m "feat: add project list page with create and card grid"
```

---

### Task 11: 项目详情页 + 图纸系列列表 + 版本时间线

**Files:**
- Create: `frontend/src/views/ProjectDetail.vue`
- Create: `frontend/src/components/DrawingSeriesList.vue`
- Create: `frontend/src/components/VersionTimeline.vue`

- [ ] **Step 1: 创建 DrawingSeriesList.vue**

```vue
<template>
  <div class="series-list">
    <div
      v-for="s in series"
      :key="s.id"
      class="series-item"
      :class="{ active: s.id === selectedId }"
      @click="$emit('select', s)"
    >
      <div class="thumb-wrapper">
        <img v-if="s.latest_version?.thumbnail_path"
          :src="thumbnailUrl(s.latest_version.id)"
          class="thumb" />
        <div v-else class="thumb-placeholder">无预览</div>
      </div>
      <div class="info">
        <span class="drawing-number">{{ s.drawing_number }}</span>
        <span class="version-badge">v{{ s.latest_version?.version_number || '?' }} · 共{{ s.version_count }}版</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { api } from '../api/index.js'
defineProps({ series: Array, selectedId: Number })
defineEmits(['select'])
function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
</script>

<style scoped>
.series-list { display: flex; flex-direction: column; gap: 8px; }
.series-item { display: flex; gap: 12px; padding: 12px; border-radius: 8px; cursor: pointer; border: 2px solid transparent; background: #fff; }
.series-item.active { border-color: #1a1a2e; }
.series-item:hover { background: #fafafa; }
.thumb-wrapper { width: 100px; height: 75px; overflow: hidden; border-radius: 4px; background: #eee; flex-shrink: 0; }
.thumb { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px; }
.info { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.drawing-number { font-weight: 600; font-size: 16px; }
.version-badge { font-size: 13px; color: #666; }
</style>
```

- [ ] **Step 2: 创建 VersionTimeline.vue**

```vue
<template>
  <div class="timeline">
    <div class="timeline-header">
      <h3>{{ series?.drawing_number || '请选择图纸' }}</h3>
      <label class="upload-btn">
        上传新版本
        <input type="file" accept=".dwg,.dxf" hidden @change="onUpload" />
      </label>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="versions.length === 0" class="empty">暂无版本，上传第一个图纸开始管理</div>

    <div v-for="v in versions" :key="v.id" class="version-item"
      :class="{ latest: v.version_number === latestVersionNumber }">
      <div class="version-header">
        <span class="version-label">
          v{{ v.version_number }}
          <span v-if="v.version_number === latestVersionNumber" class="latest-tag">当前最新</span>
        </span>
        <span class="version-date">{{ formatDate(v.created_at) }}</span>
      </div>
      <div class="version-body">
        <img v-if="v.thumbnail_path" :src="thumbnailUrl(v.id)" class="version-thumb" />
        <div v-else class="thumb-placeholder">无预览</div>
        <div class="version-info">
          <div>{{ v.filename }}</div>
          <div class="size">{{ formatSize(v.file_size) }}</div>
          <div v-if="v.change_note" class="note">"{{ v.change_note }}"</div>
        </div>
      </div>
      <div class="version-actions">
        <a :href="downloadUrl(v.id)" class="action-link">下载</a>
        <router-link
          v-if="v.version_number < latestVersionNumber"
          :to="`/compare/${v.id}/${latestVersionId}`"
          class="action-link compare-link"
        >与最新对比</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { api } from '../api/index.js'

const props = defineProps({ series: Object, projectId: Number })
const emit = defineEmits(['refresh'])

const versions = ref([])
const error = ref('')

const latestVersionNumber = computed(() =>
  versions.value.length > 0 ? versions.value[0].version_number : 0
)
const latestVersionId = computed(() =>
  versions.value.length > 0 ? versions.value[0].id : null
)

async function loadVersions() {
  if (!props.series) return
  error.value = ''
  try { versions.value = await api.listVersions(props.series.id) }
  catch (e) { error.value = e.message }
}

async function onUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  error.value = ''
  try {
    await api.uploadDrawing(props.projectId, file)
    await loadVersions()
    emit('refresh')
  } catch (e) { error.value = e.message }
  e.target.value = ''
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
function downloadUrl(vid) { return api.getDownloadUrl(vid) }
function formatDate(d) { return new Date(d).toLocaleString('zh-CN') }
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

watch(() => props.series, loadVersions)
</script>

<style scoped>
.timeline { background: #fff; border-radius: 8px; padding: 20px; border: 1px solid #e8e8e8; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.timeline-header h3 { font-size: 20px; }
.upload-btn { background: #1a1a2e; color: #fff; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.version-item { border-left: 3px solid #ddd; padding: 12px 16px; margin-bottom: 8px; border-radius: 0 6px 6px 0; }
.version-item.latest { border-left-color: #27ae60; background: #f0faf4; }
.version-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.version-label { font-weight: 600; }
.latest-tag { background: #27ae60; color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; font-weight: 400; }
.version-date { font-size: 13px; color: #999; }
.version-body { display: flex; gap: 12px; }
.version-thumb { width: 120px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; }
.thumb-placeholder { width: 120px; height: 90px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; font-size: 12px; }
.version-info { font-size: 14px; }
.version-info .size { color: #999; font-size: 13px; }
.version-info .note { color: #555; font-style: italic; margin-top: 4px; }
.version-actions { margin-top: 8px; display: flex; gap: 16px; }
.action-link { font-size: 13px; color: #1a1a2e; text-decoration: none; }
.action-link:hover { text-decoration: underline; }
.compare-link { color: #e67e22; }
.empty { color: #999; text-align: center; padding: 40px; }
.error { color: #e74c3c; padding: 8px; margin-bottom: 8px; font-size: 14px; }
</style>
```

- [ ] **Step 3: 创建 ProjectDetail.vue**

```vue
<template>
  <div>
    <router-link to="/" class="back-link">← 返回项目列表</router-link>

    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <div class="project-header">
        <h1>{{ project.name }}</h1>
      </div>

      <div class="detail-layout">
        <aside class="sidebar">
          <DrawingSeriesList
            :series="seriesList"
            :selectedId="selectedSeries?.id"
            @select="selectedSeries = $event"
          />
        </aside>
        <section class="main-area">
          <VersionTimeline
            :series="selectedSeries"
            :projectId="project.id"
            @refresh="loadProject"
          />
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import DrawingSeriesList from '../components/DrawingSeriesList.vue'
import VersionTimeline from '../components/VersionTimeline.vue'

const route = useRoute()
const project = ref(null)
const seriesList = ref([])
const selectedSeries = ref(null)
const loading = ref(true)
const error = ref('')

async function loadProject() {
  loading.value = true
  error.value = ''
  try {
    project.value = await api.getProject(route.params.id)
    seriesList.value = project.value.series_list || []
    if (selectedSeries.value) {
      const updated = seriesList.value.find(s => s.id === selectedSeries.value.id)
      selectedSeries.value = updated || seriesList.value[0] || null
    } else if (seriesList.value.length > 0) {
      selectedSeries.value = seriesList.value[0]
    }
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(loadProject)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }
.project-header { margin-bottom: 20px; }
.project-header h1 { font-size: 24px; }
.detail-layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; align-items: start; }
@media (max-width: 768px) { .detail-layout { grid-template-columns: 1fr; } }
.error { color: #e74c3c; padding: 16px; }
</style>
```

**注意**: 需要在 projects API 中让 get_project 也返回 series_list。修改 `backend/app/routes/projects.py` 的 `get_project` 函数：

```python
@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    series_out = []
    for s in project.series_list:
        versions = s.versions
        latest = None
        if versions:
            latest = DrawingVersionOut(
                id=versions[0].id,
                series_id=versions[0].series_id,
                version_number=versions[0].version_number,
                filename=versions[0].filename,
                file_hash=versions[0].file_hash,
                file_size=versions[0].file_size,
                thumbnail_path=versions[0].thumbnail_path,
                metadata_json=versions[0].metadata_json or {},
                change_note=versions[0].change_note or "",
                created_at=versions[0].created_at,
            )
        series_out.append({
            "id": s.id,
            "project_id": s.project_id,
            "drawing_number": s.drawing_number,
            "created_at": s.created_at,
            "latest_version": latest,
            "version_count": len(versions),
        })
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "series_count": len(project.series_list),
        "series_list": series_out,
    }
```

需要在 projects.py 顶部导入 `DrawingVersionOut`:
```python
from app.schemas import ProjectCreate, ProjectOut, UploadResult, DrawingVersionOut
```

- [ ] **Step 4: Commit**

```bash
cd D:/CAD管理模块 && git add frontend/src/views/ProjectDetail.vue frontend/src/components/DrawingSeriesList.vue frontend/src/components/VersionTimeline.vue backend/app/routes/projects.py
git commit -m "feat: add project detail page with series list and version timeline"
```

---

### Task 12: 版本对比页 + DiffTable + 旧版拦截

**Files:**
- Create: `frontend/src/views/VersionCompare.vue`
- Create: `frontend/src/components/DiffTable.vue`
- Create: `frontend/src/components/OldVersionWarning.vue`

- [ ] **Step 1: 创建 DiffTable.vue**

```vue
<template>
  <div class="diff-table-wrapper">
    <h4>变更明细</h4>
    <table class="diff-table">
      <thead>
        <tr>
          <th>字段</th>
          <th>v{{ oldVersionNumber }}（旧）</th>
          <th class="arrow-col"></th>
          <th>v{{ newVersionNumber }}（新）</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in diffs" :key="d.field" :class="{ changed: d.changed, unchanged: !d.changed }">
          <td class="field-label">{{ d.label }}</td>
          <td class="old-val">{{ d.old_value || '-' }}</td>
          <td class="arrow-col">
            <span v-if="d.changed" class="arrow">──▶</span>
            <span v-else class="no-change">─</span>
          </td>
          <td class="new-val">{{ d.new_value || '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({ diffs: Array, oldVersionNumber: Number, newVersionNumber: Number })
</script>

<style scoped>
.diff-table-wrapper { margin-top: 24px; }
.diff-table-wrapper h4 { margin-bottom: 12px; font-size: 16px; }
.diff-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.diff-table th { background: #f8f8f8; padding: 10px 12px; text-align: left; font-weight: 600; }
.diff-table td { padding: 10px 12px; border-bottom: 1px solid #eee; }
tr.changed { background: #fff5f5; border-left: 4px solid #e74c3c; }
tr.unchanged { border-left: 4px solid #27ae60; }
.field-label { font-weight: 500; }
.arrow { color: #e67e22; font-weight: bold; }
.no-change { color: #ccc; }
.old-val { color: #888; }
.new-val { color: #333; font-weight: 500; }
</style>
```

- [ ] **Step 2: 创建 VersionCompare.vue**

```vue
<template>
  <div>
    <router-link :to="`/project/${projectId}`" class="back-link">← 返回项目</router-link>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <h2>{{ drawingNumber }} · 版本对比</h2>

      <!-- 新版卡片 -->
      <div class="version-card new-card">
        <div class="card-badge">v{{ vNew?.version_number }} · 当前（新）</div>
        <div class="card-body">
          <img v-if="vNew?.thumbnail_path" :src="thumbnailUrl(vNew.id)" class="compare-thumb" />
          <div v-else class="thumb-placeholder">无预览</div>
          <div class="card-info">
            <div>文件名: {{ vNew?.filename }}</div>
            <div>上传: {{ formatDate(vNew?.created_at) }}</div>
            <div v-if="vNew?.change_note">变更: "{{ vNew.change_note }}"</div>
          </div>
        </div>
      </div>

      <!-- 旧版卡片 -->
      <div class="version-card old-card">
        <div class="card-badge old-badge">v{{ vOld?.version_number }} · 上一个（旧）</div>
        <div class="card-body">
          <img v-if="vOld?.thumbnail_path" :src="thumbnailUrl(vOld.id)" class="compare-thumb" />
          <div v-else class="thumb-placeholder">无预览</div>
          <div class="card-info">
            <div>文件名: {{ vOld?.filename }}</div>
            <div>上传: {{ formatDate(vOld?.created_at) }}</div>
          </div>
        </div>
      </div>

      <DiffTable :diffs="diffs" :oldVersionNumber="vOld?.version_number" :newVersionNumber="vNew?.version_number" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/index.js'
import DiffTable from '../components/DiffTable.vue'

const route = useRoute()
const vOld = ref(null)
const vNew = ref(null)
const diffs = ref([])
const drawingNumber = ref('')
const projectId = ref(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.compareVersions(route.params.vid1, route.params.vid2)
    vOld.value = data.version_old
    vNew.value = data.version_new
    diffs.value = data.diffs
    drawingNumber.value = vNew.value.drawing_number || ''
    // 获取 projectId
    const series = await api.getSeries(vNew.value.series_id)
    projectId.value = series.project_id
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

function thumbnailUrl(vid) { return api.getThumbnailUrl(vid) }
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.back-link { color: #1a1a2e; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }
h2 { font-size: 22px; margin-bottom: 20px; }
.version-card { border-radius: 8px; padding: 0; margin-bottom: 16px; overflow: hidden; }
.new-card { border: 2px solid #27ae60; }
.old-card { border: 2px dashed #ccc; }
.card-badge { padding: 8px 16px; font-weight: 600; font-size: 14px; background: #27ae60; color: #fff; }
.old-badge { background: #bbb; }
.card-body { display: flex; gap: 16px; padding: 16px; }
.compare-thumb { width: 200px; height: 150px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; flex-shrink: 0; }
.thumb-placeholder { width: 200px; height: 150px; display: flex; align-items: center; justify-content: center; background: #eee; border-radius: 4px; color: #999; }
.card-info { font-size: 14px; }
.error { color: #e74c3c; }
</style>
```

- [ ] **Step 3: 创建 OldVersionWarning.vue**

```vue
<template>
  <div v-if="visible" class="overlay" @click.self="dismiss">
    <div class="warning-dialog">
      <div class="warn-icon">⚠️</div>
      <h3>你正在查看 v{{ currentVersion }}（旧版本）</h3>
      <p>最新版本是 <strong>v{{ latestVersion }}</strong> · {{ latestDate }}</p>
      <p v-if="latestNote" class="latest-note">变更说明: "{{ latestNote }}"</p>
      <div class="warn-actions">
        <button class="btn-primary" @click="goLatest">查看最新 v{{ latestVersion }}</button>
        <button class="btn-ghost" @click="dismiss">继续看当前 v{{ currentVersion }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  visible: Boolean,
  currentVersion: Number,
  latestVersion: Number,
  latestVersionId: Number,
  latestNote: String,
  latestDate: String,
  targetPath: String,
})
const emit = defineEmits(['dismiss'])
const router = useRouter()

function goLatest() {
  if (props.targetPath) {
    router.push(props.targetPath)
  }
  emit('dismiss')
}
function dismiss() { emit('dismiss') }
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.warning-dialog { background: #fff; border-radius: 12px; padding: 32px; max-width: 440px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.2); }
.warn-icon { font-size: 40px; margin-bottom: 12px; }
.warning-dialog h3 { font-size: 18px; margin-bottom: 8px; }
.warning-dialog p { color: #666; margin-bottom: 6px; font-size: 14px; }
.latest-note { font-style: italic; color: #555; }
.warn-actions { display: flex; gap: 12px; justify-content: center; margin-top: 20px; }
.btn-primary { background: #1a1a2e; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-ghost { background: none; border: 1px solid #ccc; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; }
</style>
```

- [ ] **Step 4: 将 OldVersionWarning 集成到 VersionTimeline**

在 `VersionTimeline.vue` 的版本列表中，点击旧版本时触发警告。修改 `VersionTimeline.vue` 的 `<script setup>` 部分，添加：

```javascript
// 在 script setup 中添加
import OldVersionWarning from './OldVersionWarning.vue'

const showWarning = ref(false)
const warningData = ref({})

function onClickVersion(v) {
  if (v.version_number < latestVersionNumber.value) {
    warningData.value = {
      currentVersion: v.version_number,
      latestVersion: latestVersionNumber.value,
      latestVersionId: latestVersionId.value,
      latestNote: versions.value[0]?.change_note || '',
      latestDate: formatDate(versions.value[0]?.created_at),
      targetPath: `/compare/${v.id}/${latestVersionId.value}`,
    }
    showWarning.value = true
  }
}
```

在 template 的 `.version-item` 上添加点击事件 `@click="onClickVersion(v)"`，并在末尾添加：
```html
<OldVersionWarning v-bind="warningData" :visible="showWarning" @dismiss="showWarning = false" />
```

- [ ] **Step 5: Commit**

```bash
cd D:/CAD管理模块 && git add frontend/src/views/VersionCompare.vue frontend/src/components/DiffTable.vue frontend/src/components/OldVersionWarning.vue frontend/src/components/VersionTimeline.vue
git commit -m "feat: add version compare page with diff table and old version warning"
```

---

### Task 13: get_project 返回 series_list 的补充 + 测试修复

之前的 Task 11 中已经修改了 `projects.py` 让 `get_project` 返回 `series_list`。现在需要更新测试，确保测试不因返回结构变化而失败。

- [ ] **Step 1: 更新 test_projects.py 中的 get_project 测试**

```python
def test_get_project_with_series_list(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "测试"
    assert "series_list" in data
    assert data["series_list"] == []
```

- [ ] **Step 2: 运行所有测试**

```bash
cd D:/CAD管理模块/backend && python -m pytest tests/ -v
```

Expected: all tests pass (approximately 18 tests)

- [ ] **Step 3: Commit**

```bash
cd D:/CAD管理模块 && git add backend/
git commit -m "fix: ensure get_project returns series_list, update tests"
```

---

## 自审清单

**1. Spec 覆盖检查:**
- ✅ 项目 CRUD → Task 6
- ✅ 上传 + 版本识别 + 图号提取 → Task 7
- ✅ 图纸系列 + 版本查询 → Task 8
- ✅ 版本对比 → Task 8 (compare endpoint)
- ✅ 缩略图 → Task 5
- ✅ 文件存储 + hash → Task 4
- ✅ 项目列表页 → Task 10
- ✅ 项目详情页 + 最新版标记 → Task 11
- ✅ 版本对比页（新在上前）→ Task 12
- ✅ 旧版拦截提示 → Task 12
- ✅ DiffTable 颜色编码 → Task 12
- ✅ 错误处理（格式/大小/hash重复）→ Task 7, Task 4

**2. Placeholder 扫描:** 无 TBD、TODO、vague instructions

**3. 类型一致性:**
- `DrawingVersionOut` 定义在 Task 3，在 Task 8 的路由中构造，在 Task 11 前端中消费 → 字段名一致
- `UploadResult` 定义在 Task 3，在 Task 7 返回 → 字段名一致
- `CompareResult` 定义在 Task 3，在 Task 8 compare 端点返回，在 Task 12 前端消费 → 字段名一致
- `FieldDiff` 定义在 Task 3，在 Task 8 构造，在 Task 12 DiffTable 消费 → `field`, `label`, `old_value`, `new_value`, `changed` 一致

---

## 后续改进（非本期）

- 用户认证系统
- DWG 文件内文本/图层深度对比（依赖 ODA 库）
- 版本分支与合并
- 云端部署（Docker + Nginx）
- Electron 桌面打包

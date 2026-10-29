import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from app.database import engine, Base


def get_frontend_dir():
    """获取前端静态文件目录"""
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent

    candidates = [
        base / "frontend" / "dist",
        base.parent / "frontend" / "dist",
    ]

    for path in candidates:
        if path.exists() and (path / "index.html").exists():
            return path
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CAD Version Manager", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
from app.routes import projects, series, versions, deletions, exports, backup, smart_upload
app.include_router(projects.router, prefix="/api")
app.include_router(series.router, prefix="/api")
app.include_router(versions.router, prefix="/api")
app.include_router(deletions.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(backup.router, prefix="/api")
app.include_router(smart_upload.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/debug")
def debug():
    frontend_dir = get_frontend_dir()
    return {
        "frozen": getattr(sys, 'frozen', False),
        "executable": str(Path(sys.executable)) if hasattr(sys, 'executable') else None,
        "frontend_dir": str(frontend_dir) if frontend_dir else None,
        "frontend_exists": frontend_dir.exists() if frontend_dir else False,
    }


# 前端静态文件服务
frontend_dir = get_frontend_dir()
if frontend_dir:
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dir / "index.html")

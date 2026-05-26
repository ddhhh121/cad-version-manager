from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base


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

from app.routes import projects
app.include_router(projects.router, prefix="/api")
from app.routes import series, versions
app.include_router(series.router, prefix="/api")
app.include_router(versions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}

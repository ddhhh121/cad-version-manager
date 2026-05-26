from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CAD Version Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route imports will be added in later tasks:
# from app.routes import projects, series, versions
# app.include_router(projects.router, prefix="/api")
# app.include_router(series.router, prefix="/api")
# app.include_router(versions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DrawingSeries, DrawingVersion
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

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DeletionLog, Project, DrawingSeries, DrawingVersion
from app.schemas import DeletionLogOut

router = APIRouter(tags=["deletions"])


@router.get("/deletions", response_model=list[DeletionLogOut])
def list_deletions(
    entity_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(DeletionLog)
    if entity_type:
        q = q.filter(DeletionLog.entity_type == entity_type)
    q = q.order_by(DeletionLog.deleted_at.desc())
    return q.offset(offset).limit(limit).all()


@router.post("/deletions/{log_id}/restore")
def restore_deletion(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DeletionLog).filter(DeletionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="删除记录不存在")

    data = log.entity_data or {}

    if log.entity_type == "project":
        project = Project(
            id=log.entity_id,
            name=log.entity_name,
            description=data.get("description", ""),
        )
        db.add(project)
        db.flush()

    elif log.entity_type == "series":
        series = DrawingSeries(
            id=log.entity_id,
            project_id=data.get("project_id"),
            drawing_number=log.entity_name,
        )
        db.add(series)
        db.flush()

    elif log.entity_type == "version":
        version = DrawingVersion(
            id=log.entity_id,
            series_id=data.get("series_id"),
            version_number=data.get("version_number", 0),
            filename=data.get("filename", ""),
            file_hash=data.get("file_hash", ""),
            file_path=data.get("file_path", ""),
            file_size=data.get("file_size", 0),
            thumbnail_path=data.get("thumbnail_path"),
            metadata_json=data.get("metadata_json", {}),
            change_note=data.get("change_note", ""),
        )
        db.add(version)
        db.flush()

    else:
        raise HTTPException(status_code=400, detail="不支持的实体类型")

    db.delete(log)
    db.commit()
    return {"status": "ok", "entity_type": log.entity_type, "entity_id": log.entity_id}

import shutil

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DrawingSeries, DrawingVersion, DeletionLog
from app.schemas import DrawingVersionOut, ChangeNoteUpdate, TagsUpdate, CompareResult, FieldDiff
from app.config import UPLOAD_DIR
from app.services.preview_service import generate_preview

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
        tags=v.tags or [],
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


@router.put("/versions/{version_id}/tags")
def update_tags(
    version_id: int,
    body: TagsUpdate,
    db: Session = Depends(get_db),
):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")
    v.tags = body.tags
    db.commit()
    return {"status": "ok"}


@router.get("/compare/{vid1}/{vid2}", response_model=CompareResult)
def compare_versions(vid1: int, vid2: int, db: Session = Depends(get_db)):
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

    # 基础字段 diff (insert at beginning)
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


@router.delete("/versions/{version_id}")
def delete_version(version_id: int, db: Session = Depends(get_db)):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")

    series_id = v.series_id
    project_id = v.series.project_id

    # 记录删除日志
    log = DeletionLog(
        entity_type="version",
        entity_id=v.id,
        entity_name=v.filename,
        entity_data={
            "series_id": v.series_id,
            "version_number": v.version_number,
            "filename": v.filename,
            "file_hash": v.file_hash,
            "file_path": v.file_path,
            "file_size": v.file_size,
            "thumbnail_path": v.thumbnail_path,
            "metadata_json": v.metadata_json or {},
            "change_note": v.change_note or "",
        },
    )
    db.add(log)

    file_path = UPLOAD_DIR / v.file_path
    if file_path.exists():
        file_path.unlink()

    if v.thumbnail_path:
        thumb_path = UPLOAD_DIR / v.thumbnail_path
        if thumb_path.exists():
            thumb_path.unlink()

    remaining = db.query(DrawingVersion).filter(
        DrawingVersion.series_id == series_id,
        DrawingVersion.id != version_id,
    ).count()

    db.delete(v)

    series_deleted = False
    if remaining == 0:
        series = db.query(DrawingSeries).filter(DrawingSeries.id == series_id).first()
        if series:
            series_dir = UPLOAD_DIR / "projects" / str(project_id) / str(series_id)
            if series_dir.exists():
                shutil.rmtree(series_dir)
            db.delete(series)
            series_deleted = True

    db.commit()
    return {"status": "ok", "series_deleted": series_deleted}


@router.get("/versions/{version_id}/preview")
def preview_version(version_id: int, db: Session = Depends(get_db)):
    v = db.query(DrawingVersion).filter(DrawingVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="版本不存在")

    full_path = UPLOAD_DIR / v.file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    result = generate_preview(str(full_path))
    return result

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

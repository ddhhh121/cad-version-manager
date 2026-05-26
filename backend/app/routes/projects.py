from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, DrawingSeries, DrawingVersion
from app.schemas import ProjectCreate, ProjectOut, UploadResult, DrawingVersionOut
from app.config import UPLOAD_DIR
from app.services.file_service import validate_file, compute_hash, save_file
from app.services.drawing_service import extract_drawing_number, extract_metadata_from_dxf
from app.services.thumbnail_service import generate_thumbnail

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
            v = versions[0]
            latest = DrawingVersionOut(
                id=v.id, series_id=v.series_id,
                version_number=v.version_number, filename=v.filename,
                file_hash=v.file_hash, file_size=v.file_size,
                thumbnail_path=v.thumbnail_path,
                metadata_json=v.metadata_json or {},
                change_note=v.change_note or "",
                created_at=v.created_at,
            )
        series_out.append({
            "id": s.id, "project_id": s.project_id,
            "drawing_number": s.drawing_number,
            "created_at": s.created_at,
            "latest_version": latest,
            "version_count": len(versions),
        })

    return {
        "id": project.id, "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "series_count": len(project.series_list),
        "series_list": series_out,
    }


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

    # DXF 元数据 (only for .dxf files)
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

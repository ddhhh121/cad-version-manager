"""
智能上传 API - 自动识别图纸新旧并归类
"""
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import Project, DrawingSeries, DrawingVersion
from app.schemas import UploadResult
from app.config import UPLOAD_DIR
from app.services.file_service import validate_file, compute_hash, save_file
from app.services.drawing_service import extract_drawing_number
from app.services.thumbnail_service import generate_thumbnail

router = APIRouter(tags=["smart-upload"])


@router.post("/smart-upload")
def smart_upload(
    file: UploadFile = File(...),
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    智能上传：
    1. 从文件名提取图纸编号
    2. 在所有项目中查找匹配的系列
    3. 如果找到：检查是否重复，不重复则添加为新版本
    4. 如果未找到：创建新项目和系列
    """
    content = file.file.read()
    err = validate_file(file.filename, content)
    if err:
        raise HTTPException(status_code=400, detail=err)

    file_hash = compute_hash(content)
    drawing_number = extract_drawing_number(file.filename)

    # 查找已有的系列（在指定项目或所有项目中）
    query = db.query(DrawingSeries).filter(
        DrawingSeries.drawing_number == drawing_number
    )
    if project_id:
        query = query.filter(DrawingSeries.project_id == project_id)

    series = query.first()
    is_new_series = series is None
    target_project_id = project_id

    if is_new_series:
        # 创建新系列
        if not target_project_id:
            # 查找或创建默认项目
            default_project = db.query(Project).filter(
                Project.name == "默认项目"
            ).first()
            if not default_project:
                default_project = Project(name="默认项目", description="自动创建的默认项目")
                db.add(default_project)
                db.flush()
            target_project_id = default_project.id

        series = DrawingSeries(
            project_id=target_project_id,
            drawing_number=drawing_number
        )
        db.add(series)
        db.flush()
    else:
        target_project_id = series.project_id
        # 检查是否完全相同的文件
        dup = db.query(DrawingVersion).filter(
            DrawingVersion.series_id == series.id,
            DrawingVersion.file_hash == file_hash,
        ).first()
        if dup:
            return {
                "status": "duplicate",
                "message": f"文件已存在：{drawing_number} v{dup.version_number}",
                "series_id": series.id,
                "version_id": dup.id,
                "version_number": dup.version_number,
                "drawing_number": drawing_number,
                "is_new_series": False,
                "filename": file.filename,
            }

    # 计算版本号
    max_v = db.query(DrawingVersion.version_number).filter(
        DrawingVersion.series_id == series.id
    ).order_by(DrawingVersion.version_number.desc()).first()
    version_number = (max_v[0] + 1) if max_v else 1

    # 存储文件
    file_path = save_file(target_project_id, series.id, version_number, file.filename, content)

    # 缩略图
    thumb_path = generate_thumbnail(str(UPLOAD_DIR / file_path))

    version = DrawingVersion(
        series_id=series.id,
        version_number=version_number,
        filename=file.filename,
        file_hash=file_hash,
        file_path=file_path,
        file_size=len(content),
        thumbnail_path=thumb_path,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    # 获取项目名称
    project = db.query(Project).filter(Project.id == target_project_id).first()

    return {
        "status": "new_version" if not is_new_series else "new_series",
        "message": f"{'新系列已创建' if is_new_series else '新版本已添加'}：{drawing_number} v{version_number}",
        "series_id": series.id,
        "version_id": version.id,
        "version_number": version.version_number,
        "drawing_number": drawing_number,
        "project_id": target_project_id,
        "project_name": project.name if project else "未知项目",
        "is_new_series": is_new_series,
        "filename": file.filename,
        "file_size": len(content),
    }


@router.post("/smart-upload-batch")
def smart_upload_batch(
    files: list[UploadFile] = File(...),
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    """批量智能上传"""
    results = []
    for file in files:
        try:
            result = smart_upload(file=file, project_id=project_id, db=db)
            results.append(result)
        except HTTPException as e:
            results.append({
                "status": "error",
                "message": str(e.detail),
                "filename": file.filename,
            })
        except Exception as e:
            results.append({
                "status": "error",
                "message": str(e),
                "filename": file.filename,
            })
    return {"results": results}

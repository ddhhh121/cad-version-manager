from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, DrawingSeries, DrawingVersion
from app.schemas import DrawingVersionOut
from app.services.export_service import generate_excel, generate_pdf

router = APIRouter(tags=["exports"])


def _version_to_dict(v: DrawingVersion) -> dict:
    return {
        "id": v.id,
        "series_id": v.series_id,
        "version_number": v.version_number,
        "filename": v.filename,
        "file_hash": v.file_hash,
        "file_size": v.file_size,
        "thumbnail_path": v.thumbnail_path,
        "metadata_json": v.metadata_json or {},
        "change_note": v.change_note or "",
        "tags": v.tags or [],
        "created_at": v.created_at.isoformat() if v.created_at else "",
    }


@router.get("/export/project/{project_id}")
def export_project(
    project_id: int,
    format: str = Query("excel", regex="^(excel|pdf)$"),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 收集数据
    data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "series_list": [],
    }

    for series in project.series_list:
        series_data = {
            "id": series.id,
            "drawing_number": series.drawing_number,
            "versions": [_version_to_dict(v) for v in series.versions],
        }
        data["series_list"].append(series_data)

    # 生成文件
    if format == "excel":
        content = generate_excel(data, "project")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{project.name}_版本历史.xlsx"
    else:
        content = generate_pdf(data, "project")
        media_type = "application/pdf"
        filename = f"{project.name}_版本历史.pdf"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/series/{series_id}")
def export_series(
    series_id: int,
    format: str = Query("excel", regex="^(excel|pdf)$"),
    db: Session = Depends(get_db),
):
    series = db.query(DrawingSeries).filter(DrawingSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="图纸系列不存在")

    # 收集数据
    data = {
        "id": series.id,
        "drawing_number": series.drawing_number,
        "versions": [_version_to_dict(v) for v in series.versions],
    }

    # 生成文件
    if format == "excel":
        content = generate_excel(data, "series")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{series.drawing_number}_版本历史.xlsx"
    else:
        content = generate_pdf(data, "series")
        media_type = "application/pdf"
        filename = f"{series.drawing_number}_版本历史.pdf"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

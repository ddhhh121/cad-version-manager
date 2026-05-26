from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectOut

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


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        series_count=len(project.series_list),
    )

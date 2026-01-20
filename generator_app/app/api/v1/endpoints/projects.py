import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID

from generator_app.app.core.database import get_db
from generator_app.app.core.generator.code_generator import CodeGenerator
from generator_app.app.core.security import get_current_user
from generator_app.app.models.project import Project
from generator_app.app.models.project_version import ProjectVersion
from generator_app.app.models.project_collaborator import ProjectCollaborator
from generator_app.app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectListItem
)
from generator_app.app.schemas.project_version import ProjectVersionRead
from generator_app.app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectRead)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validar slug único
    existing = db.query(Project).filter(Project.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        definition_json=payload.definition_json,
        is_public=payload.is_public
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Crear versión inicial
    version = ProjectVersion(
        project_id=project.id,
        version=1,
        definition_json=payload.definition_json
    )
    db.add(version)
    db.commit()

    return project
@router.get("/", response_model=list[ProjectListItem])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validar permisos
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(status_code=403, detail="Not authorized")

    return project

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Actualizar campos
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    # Crear nueva versión si cambió el JSON
    if payload.definition_json:
        latest_version = (
            db.query(ProjectVersion)
            .filter(ProjectVersion.project_id == project.id)
            .order_by(ProjectVersion.version.desc())
            .first()
        )
        new_version = ProjectVersion(
            project_id=project.id,
            version=(latest_version.version + 1),
            definition_json=payload.definition_json
        )
        db.add(new_version)
        db.commit()

    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(project)
    db.commit()

    return {"detail": "Project deleted"}

@router.get("/{project_id}/versions", response_model=list[ProjectVersionRead])
def list_versions(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    versions = (
        db.query(ProjectVersion)
        .filter(ProjectVersion.project_id == project_id)
        .order_by(ProjectVersion.version.desc())
        .all()
    )

    return versions

@router.post("/{project_id}/share")
def share_project(
    project_id: UUID,
    user_id: UUID,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    collaborator = ProjectCollaborator(
        project_id=project_id,
        user_id=user_id,
        role=role
    )

    db.add(collaborator)
    db.commit()

    return {"detail": "Project shared"}

@router.post("/{project_id}/generate")
def generate_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Buscar el proyecto
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Validar permisos
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3. Extraer el JSON de definición
    definition = project.definition_json

    # 4. Crear carpeta temporal para generar el ZIP
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = CodeGenerator(
            project_definition=definition,
            output_dir=tmpdir
        )

        zip_path = generator.generate_zip()

        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="ZIP generation failed")

        # 5. Devolver el ZIP como FileResponse
        return FileResponse(
            path=zip_path,
            filename=f"{project.slug}.zip",
            media_type="application/zip"
        )

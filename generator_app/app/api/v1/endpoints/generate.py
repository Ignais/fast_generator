from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from generator_app.app.core.logging_config import logger
from generator_app.app.schemas.project import GenerateRequest
from generator_app.app.workers.normalizer import normalize_project_definition
from generator_app.app.core.generator.code_generator import CodeGenerator
from generator_app.app.core.security import require_permission

router = APIRouter(prefix="/generator", tags=["Generator"])

@router.post("/", dependencies=[Depends(require_permission("project:create"))])
@router.post("/")
async def generate_project(
    payload: GenerateRequest = Body(...)
):
    try:
        # 1) Unificar la fuente de datos (AI vs manual)
        if payload.definition_json is not None:
            # AI mode
            raw = payload.definition_json
            project_raw = raw.get("project", {}) or {}
            models_raw = raw.get("models", {}) or {}
        else:
            # Manual mode
            if payload.project is None or payload.models is None:
                raise HTTPException(
                    status_code=422,
                    detail="Either 'definition_json' or both 'project' and 'models' must be provided.",
                )
            project_raw = payload.project
            models_raw = payload.models

        # 2) Normalizar para el CodeGenerator
        normalized = normalize_project_definition({
            "project": project_raw,
            "models": models_raw,
        })

        project_def = normalized["project"]
        models_def = normalized["models"]

        # 3) Generar proyecto
        BASE_DIR = Path(__file__).resolve().parents[3]
        DOWNLOADS_DIR = BASE_DIR / "downloads"
        DOWNLOADS_DIR.mkdir(exist_ok=True)

        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_dir = tmpdir_path / "generated_project"
            output_dir.mkdir(parents=True, exist_ok=True)

            templates_dir = BASE_DIR / "core" / "templates"

            gen = CodeGenerator(templates_dir=templates_dir, output_dir=output_dir)
            gen.generate_project_structure(project_def, models_def)

            zip_name = f"{project_def['project_name']}.zip"
            final_zip_path = DOWNLOADS_DIR / zip_name

            shutil.make_archive(final_zip_path.with_suffix(""), "zip", output_dir)

            return FileResponse(
                path=str(final_zip_path),
                filename=zip_name,
                media_type="application/zip",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating project: {e}")

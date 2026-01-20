from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil

from generator_app.app.core.generator.code_generator import CodeGenerator

router = APIRouter(prefix="/generate", tags=["Generator"])


class GenerateRequest(BaseModel):
    project: Dict[str, Any]
    models: List[Dict[str, Any]]


@router.post("/project")
async def generate_project(payload: GenerateRequest):
    try:
        # 1. Carpeta persistente donde guardar ZIPs
        BASE_DIR = Path(__file__).resolve().parents[3]
        DOWNLOADS_DIR = BASE_DIR / "downloads"
        DOWNLOADS_DIR.mkdir(exist_ok=True)

        project_def = payload.project 
        models_def = payload.models or [] # nunca insertar {}
        if not isinstance(project_def, dict): 
            raise ValueError("El campo 'project' debe ser un objeto JSON") 

        if not isinstance(models_def, list): 
            raise ValueError("El campo 'models' debe ser una lista")

        # 2. Carpeta temporal para generar el proyecto
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            output_dir = tmpdir_path / "generated_project"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 3. Ruta de plantillas
            templates_dir = BASE_DIR / "core" / "templates"

            # 4. Generar el proyecto
            gen = CodeGenerator(templates_dir=templates_dir, output_dir=output_dir)
            gen.generate_project_structure(payload.project, payload.models)

            # 5. Crear ZIP en carpeta persistente
            zip_name = f"{payload.project.project_name}.zip"
            final_zip_path = DOWNLOADS_DIR / zip_name

            shutil.make_archive(final_zip_path.with_suffix(""), "zip", output_dir)

            return FileResponse(
                path=str(final_zip_path),
                filename=zip_name,
                media_type="application/zip",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating project: {e}")


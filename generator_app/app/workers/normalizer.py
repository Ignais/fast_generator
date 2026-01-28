import re
from typing import Dict, Any, List
from generator_app.app.workers.mtm_validator import validate_many_to_many

def _normalize_project_block(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza el bloque 'project' combinando tu lógica anterior
    con lo que necesitamos ahora.
    """

    normalized_project = {
        "project_name": project.get("project_name")
            or project.get("name")
            or project.get("app_name")
            or "my_app",
        "version": project.get("version", "1.0.0"),
        "description": project.get("description", "Generated FastAPI project"),
        "mode": project.get("mode", "sync"),  # tu CodeGenerator usa 'sync' / 'async'
        "backend": project.get("backend", "fastapi"),
        "frontend": project.get("frontend", "none"),
        "dependencies": project.get("dependencies", ["fastapi", "uvicorn"]),
        "routes": project.get("routes", []),
        "env": project.get("env", {}),
        "database": project.get("database") or {
            "engine": "sqlite",
            "database": "database.db",
        },
    }

    # dependencies como dict → lista
    deps = normalized_project["dependencies"]
    if isinstance(deps, dict):
        # si vienen con versiones, las mantenemos en formato "pkg==version"
        normalized_project["dependencies"] = [
            f"{name}=={version}" for name, version in deps.items()
        ]

    # routes como lista de strings → lista de dicts
    routes = normalized_project["routes"]
    if isinstance(routes, list) and all(isinstance(r, str) for r in routes):
        normalized_project["routes"] = [
            {
                "path": f"/{r}",
                "methods": ["GET"],
                "description": f"Auto route for {r}",
            }
            for r in routes
        ]

    return normalized_project


def _infer_field_from_kv(field_name: str, field_type: str, models_keys: List[str]) -> Dict[str, Any]:
    """
    Convierte un par clave-valor del estilo:
      "id": "int"
      "projects": "List[Project]"
      "user": "User"
    en un field estructurado para CodeGenerator.
    """

    # List[Model] → relación (lado "uno" o "muchos")
    list_match = re.match(r"List\[(\w+)]", field_type)
    if list_match:
        target = list_match.group(1)
        return {
            "name": field_name,
            "type": "relationship",
            "relationship": field_name,
            "target": target,
            "back_populates": None,  # se puede completar luego si quieres
        }

    # Campo que apunta a otro modelo → relación
    if field_type in models_keys:
        return {
            "name": field_name,
            "type": "relationship",
            "relationship": field_name,
            "target": field_type,
            "back_populates": None,
        }

    # Campo normal
    # Ajuste de tipos "integer"/"string" → "int"/"str"
    if field_type == "integer":
        field_type = "int"
    elif field_type == "string":
        field_type = "str"

    return {
        "name": field_name,
        "type": field_type,
        "primary_key": field_name == "id",
    }


def _normalize_models_block(models: Any) -> List[Dict[str, Any]]:
    """
    Normaliza el bloque 'models' para que siempre sea una lista de modelos
    con estructura compatible con CodeGenerator.
    """

    normalized_models: List[Dict[str, Any]] = []

    # Caso 1: viene como dict → {"User": {...}, "Project": {...}}
    if isinstance(models, dict):
        models_dict = models
    # Caso 2: ya viene como lista de modelos
    elif isinstance(models, list):
        # si ya vienen con "name" y "fields", los respetamos
        if all(isinstance(m, dict) and "name" in m for m in models):
            return models
        # si vienen como lista pero sin "name", no podemos inferir bien
        models_dict = {}
    else:
        models_dict = {}

    model_names = list(models_dict.keys())

    for model_name, model_body in models_dict.items():
        # si ya viene en formato estructurado, lo respetamos
        if isinstance(model_body, dict) and "fields" in model_body:
            # normalizar tipos básicos dentro de fields
            fields = model_body.get("fields", [])
            for f in fields:
                t = f.get("type")
                if t == "integer":
                    f["type"] = "int"
                elif t == "string":
                    f["type"] = "str"
            normalized_models.append(model_body)
            continue

        # caso IA: {"id": "int", "name": "str", "projects": "List[Project]"}
        if not isinstance(model_body, dict):
            continue

        fields_struct: List[Dict[str, Any]] = []

        for field_name, field_type in model_body.items():
            if not isinstance(field_type, str):
                continue
            field_def = _infer_field_from_kv(field_name, field_type, model_names)
            fields_struct.append(field_def)

        normalized_models.append(
            {
                "name": model_name,
                "table_name": model_name.lower(),
                "fields": fields_struct,
                "routes": {
                    "generate_crud": True,
                    "prefix": f"/{model_name.lower()}s",
                    "tags": [model_name],
                },
                "many_to_many": [],
            }
        )

    # Validación opcional de many-to-many si ya existiera estructura
    validate_many_to_many(normalized_models)

    return normalized_models


def normalize_project_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizador v2:
    - combina tu lógica anterior
    - añade transformación estructural para el JSON de la IA
    - deja listo para CodeGenerator
    """

    project = definition.get("project", {}) or {}
    models = definition.get("models", {}) or {}

    normalized_project = _normalize_project_block(project)
    normalized_models = _normalize_models_block(models)

    return {
        "project": normalized_project,
        "models": normalized_models,
    }

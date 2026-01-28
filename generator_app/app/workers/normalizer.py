from typing import Dict, Any, List
import re

from generator_app.app.workers.mtm_validator import validate_many_to_many


def _infer_field_from_kv(field_name: str, field_type: str, models_keys: List[str]):
    """
    Convert simple key-value definitions into structured fields.
    Relationship fields MUST NOT include 'type'.
    """

    # List[Model] → One-to-Many
    list_match = re.match(r"List\[(\w+)]", field_type)
    if list_match:
        target = list_match.group(1)
        return None, {
            "name": field_name,
            "relationship": field_name,
            "target": target,
            "back_populates": None,
            "foreign_key": None,
        }

    # Direct reference → Many-to-One
    if field_type in models_keys:
        return None, {
            "name": field_name,
            "relationship": field_name,
            "target": field_type,
            "back_populates": None,
            "foreign_key": None,
        }

    # Normal field
    if field_type == "integer":
        field_type = "int"
    elif field_type == "string":
        field_type = "str"

    return {
        "name": field_name,
        "type": field_type,
        "primary_key": field_name == "id",
    }, None


def _normalize_models_block(models: Any) -> List[Dict[str, Any]]:
    normalized_models: List[Dict[str, Any]] = []

    # Dict format: {"User": {...}}
    if isinstance(models, dict):
        models_dict = models
    else:
        models_dict = {}

    model_names = list(models_dict.keys())

    for model_name, model_body in models_dict.items():

        fields_struct: List[Dict[str, Any]] = []
        relationships_struct: List[Dict[str, Any]] = []

        # Case: already structured
        if isinstance(model_body, dict) and "fields" in model_body:
            for f in model_body["fields"]:
                # Clean invalid relationship type
                if f.get("type") == "relationship":
                    f.pop("type", None)

                if "relationship" in f:
                    relationships_struct.append(f)
                else:
                    fields_struct.append(f)

            normalized_models.append({
                "name": model_name,
                "table_name": model_name.lower(),
                "fields": fields_struct,
                "relationships": relationships_struct,
                "many_to_many": [],
            })
            continue

        # Case: AI simple dict
        if not isinstance(model_body, dict):
            continue

        for field_name, field_type in model_body.items():
            if not isinstance(field_type, str):
                continue

            field_def, rel_def = _infer_field_from_kv(field_name, field_type, model_names)

            if field_def:
                fields_struct.append(field_def)
            if rel_def:
                relationships_struct.append(rel_def)

        normalized_models.append({
            "name": model_name,
            "table_name": model_name.lower(),
            "fields": fields_struct,
            "relationships": relationships_struct,
            "many_to_many": [],
        })

    # Validate M2M
    warnings = []
    validate_many_to_many(normalized_models, warnings)

    return normalized_models


def normalize_project_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    project = definition.get("project", {}) or {}
    models = definition.get("models", {}) or {}

    normalized_models = _normalize_models_block(models)

    normalized_project = {
        "project_name": project.get("project_name") or project.get("name") or "my_app",
        "version": project.get("version", "1.0.0"),
        "description": project.get("description", "Generated FastAPI project"),
        "mode": project.get("mode", "sync"),
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

    return {
        "project": normalized_project,
        "models": normalized_models,
        "warnings": [],
    }

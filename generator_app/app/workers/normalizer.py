from generator_app.app.workers.mtm_validator import validate_many_to_many

def normalize_project_definition(definition: dict) -> dict:
    warnings = []

    project = definition.get("project", {})
    models = definition.get("models", [])

    # --- Normalizar PROJECT ---
    normalized_project = {
        "project_name": project.get("project_name")
            or project.get("name")
            or project.get("app_name")
            or "MyApp",
        "version": project.get("version", "1.0.0"),
        "description": project.get("description", "Generated FastAPI project"),
        "mode": project.get("mode", "api"),
        "backend": project.get("backend", "fastapi"),
        "frontend": project.get("frontend", "none"),
        "dependencies": project.get("dependencies", ["fastapi", "uvicorn"]),
        "routes": project.get("routes", []),
        "env": project.get("env", {}),
        "database": project.get("database") or "sqlite",
    }

    # --------------------------
    # FIX 1: dependencies como dict → lista
    # --------------------------
    deps = normalized_project["dependencies"]
    if isinstance(deps, dict):
        warnings.append("Las dependencias venían como objeto. Se convirtieron a lista.")
        normalized_project["dependencies"] = list(deps.keys())

    # --------------------------
    # FIX 2: routes como lista de strings → lista de dicts
    # --------------------------
    routes = normalized_project["routes"]
    if isinstance(routes, list) and all(isinstance(r, str) for r in routes):
        warnings.append("Las rutas venían como lista de strings. Se convirtieron a objetos.")
        normalized_project["routes"] = [
            {
                "path": f"/{r}",
                "methods": ["GET"],
                "description": f"Auto route for {r}"
            }
            for r in routes
        ]

    # --------------------------
    # Normalizar MODELS
    # --------------------------
    normalized_models = []

    if isinstance(models, dict):
        warnings.append("La IA devolvió 'models' como objeto. Se convirtió a lista.")
        models = [{"name": k, **v} for k, v in models.items()]

    for model in models:
        name = model.get("name")
        if not name:
            warnings.append("Un modelo no tenía nombre. Se ignoró.")
            continue

        fields = model.get("fields", [])
        relationships = model.get("relationships", [])

        # Normalizar tipos
        for f in fields:
            t = f.get("type")
            if t == "integer":
                f["type"] = "int"
            elif t == "string":
                f["type"] = "str"

        normalized_models.append({
            "name": name,
            "fields": fields,
            "relationships": relationships
        })

    return {
        "project": normalized_project,
        "models": normalized_models,
        "warnings": warnings
    }

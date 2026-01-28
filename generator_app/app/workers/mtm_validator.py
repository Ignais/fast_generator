def validate_many_to_many(models: list, warnings: list = None):
    model_names = {m["name"] for m in models}

    for model in models:
        for rel in model.get("relationships", []):
            if rel.get("type") != "many_to_many":
                continue

            target = rel.get("model")

            # 1. Validar que el modelo destino exista
            if target not in model_names:
                warnings.append(
                    f"Relación ManyToMany inválida: '{model['name']}' → '{target}' no existe."
                )
                continue

            # 2. Validar reciprocidad
            reciprocal_found = False
            for m2 in models:
                if m2["name"] == target:
                    for r2 in m2.get("relationships", []):
                        if r2.get("type") == "many_to_many" and r2.get("model") == model["name"]:
                            reciprocal_found = True

            if not reciprocal_found:
                warnings.append(
                    f"La relación ManyToMany '{model['name']}' → '{target}' no es recíproca. "
                    f"Se recomienda agregar la relación inversa."
                )

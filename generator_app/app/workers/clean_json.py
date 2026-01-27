import re
import json

def extract_json(text: str):
    clean = text.strip()

    clean = re.sub(r"^```[a-zA-Z]*", "", clean)
    clean = re.sub(r"```$", "", clean)

    clean = clean.strip()

    return json.loads(clean)

def clean_json_output(raw: str) -> str:
    """
    Limpia el contenido devuelto por la IA:
    - elimina bloques ```json o ```
    - elimina espacios y saltos innecesarios
    - deja solo el JSON puro
    """

    cleaned = raw.strip()

    # eliminar bloques ```json ... ```
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        # a veces queda "json\n{...}"
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    # eliminar triple backticks internos
    cleaned = cleaned.replace("```", "").strip()

    return cleaned

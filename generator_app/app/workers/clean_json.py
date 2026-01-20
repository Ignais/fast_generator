import re
import json

def extract_json(text: str):
    clean = text.strip()

    clean = re.sub(r"^```[a-zA-Z]*", "", clean)
    clean = re.sub(r"```$", "", clean)

    clean = clean.strip()

    return json.loads(clean)

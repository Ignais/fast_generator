def extract_ai_content(response):
    """
    Extrae el contenido del mensaje desde cualquier proveedor compatible con OpenAI API.
    Soporta: OpenAI, OpenRouter, Hyperbolic, DeepInfra, Together, Mistral, Groq.
    """

    # Caso 1: respuesta tipo objeto (OpenAI SDK)
    if hasattr(response, "choices"):
        choice = response.choices[0]

        # OpenAI / OpenRouter / Hyperbolic
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            return choice.message.content

        # DeepInfra / Together (texto plano)
        if hasattr(choice, "text"):
            return choice.text

    # Caso 2: respuesta tipo dict
    if isinstance(response, dict):

        # OpenAI / OpenRouter / Hyperbolic
        if "choices" in response:
            choice = response["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]

            if "text" in choice:
                return choice["text"]

        # TogetherAI (estructura distinta)
        if "output" in response and "choices" in response["output"]:
            choice = response["output"]["choices"][0]
            if "text" in choice:
                return choice["text"]

    # Fallback final
    return str(response)

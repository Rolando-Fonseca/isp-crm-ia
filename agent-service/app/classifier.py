from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from app.whatsapp import InboundMessage

Intent = Literal[
    "consulta_general",
    "quiere_aplicar",
    "pregunta_visado",
    "hablar_con_humano",
    "otro",
]


class Classification(BaseModel):
    intent: Intent = Field(description="Intención principal del último mensaje del estudiante.")
    confidence: float = Field(description="Confianza en la intención, entre 0 y 1.")
    country_of_interest: str | None = Field(
        description="País donde el estudiante quiere estudiar, en español, si lo menciona. Si no, null."
    )
    reply: str = Field(description="Respuesta que se enviará por WhatsApp al estudiante.")


class ClassificationUnavailable(Exception):
    """El modelo no devolvió una clasificación utilizable."""


SYSTEM_PROMPT = """Eres el asistente de primer contacto de una agencia que ayuda a estudiantes \
latinoamericanos a estudiar en el extranjero. Recibes el historial reciente de una conversación de \
WhatsApp y el último mensaje del estudiante. Debes clasificar la intención del último mensaje y \
redactar la respuesta que se le enviará.

Intenciones posibles:
- consulta_general: información general sobre programas, países, costos o cómo funciona el servicio.
- quiere_aplicar: quiere iniciar o avanzar una aplicación a un programa o universidad.
- pregunta_visado: dudas sobre visa, permisos o documentos migratorios.
- hablar_con_humano: pide explícitamente hablar con un asesor o una persona.
- otro: saludos sueltos, mensajes sin relación o que no encajan en las anteriores.

Reglas para la respuesta:
- Español neutro, tono cálido y breve: máximo tres frases.
- No inventes precios, fechas, requisitos ni nombres de universidades. Si no lo sabes, di que un \
asesor lo confirmará.
- Si la intención es hablar_con_humano, confirma que un asesor le escribirá pronto.
- Si el estudiante menciona un país de destino, extráelo en country_of_interest (solo el nombre del \
país en español)."""


def build_user_prompt(message: InboundMessage, history: list[dict]) -> str:
    lines = []
    for item in history:
        speaker = "Estudiante" if item["direction"] == "INBOUND" else "Agencia"
        lines.append(f"{speaker}: {item['body']}")
    transcript = "\n".join(lines) if lines else "(sin mensajes anteriores)"
    name = message.name or "sin nombre"
    return (
        f"Historial reciente:\n{transcript}\n\n"
        f"Último mensaje del estudiante ({name}):\n{message.text}"
    )


class IntentClassifier:
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def classify(self, message: InboundMessage, history: list[dict]) -> Classification:
        response = await self._client.messages.parse(
            model=self._model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": build_user_prompt(message, history)}],
            output_format=Classification,
        )
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise ClassificationUnavailable(f"stop_reason={response.stop_reason}")

        result = response.parsed_output
        result.confidence = min(1.0, max(0.0, result.confidence))
        return result

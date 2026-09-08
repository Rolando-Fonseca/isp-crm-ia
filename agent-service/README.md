# agent-service

Servicio Python (FastAPI) que recibe el webhook de Meta WhatsApp Cloud API,
registra cada mensaje como lead/mensaje en el CRM (`crm-web`), clasifica la
intención con Claude y responde por WhatsApp. Corre como proceso independiente
del CRM (ver `DOCS/01-arquitectura.md`).

## Correr en local

```bash
cd agent-service
python -m venv .venv
.venv/Scripts/activate        # Windows (en bash: source .venv/Scripts/activate)
pip install -r requirements.txt
cp .env.example .env          # ajustar claves; META_WHATSAPP_TOKEN y ANTHROPIC_API_KEY pueden quedar vacios
uvicorn app.main:app --port 8002 --reload
```

Con el CRM corriendo en `http://localhost:3002`, simular un mensaje entrante:

```bash
python scripts/send_test_message.py --phone 5491155550199 --name "Ana Pérez" --text "Hola, quiero estudiar en Canadá"
```

El lead aparece en `http://localhost:3002/leads` en la columna **Consulta**.

## Tests

```bash
pytest
```

## Endpoints

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/health` | Healthcheck |
| `GET` | `/webhook` | Verificación del webhook por Meta (`hub.verify_token`) |
| `POST` | `/webhook` | Recepción de mensajes; valida `X-Hub-Signature-256` con `META_APP_SECRET` |

## Flujo por mensaje

1. `POST /api/whatsapp/inbound` del CRM: crea el lead si no existe, guarda el
   mensaje y devuelve el historial reciente. Si el `waMessageId` ya existía
   (reintento de Meta) se corta aquí.
2. **Clasificador** (`app/classifier.py`, solo si hay `ANTHROPIC_API_KEY`):
   una llamada a Claude con salida estructurada (`messages.parse` + Pydantic)
   que devuelve `intent`, `confidence`, `country_of_interest` y la `reply`.
   Intenciones: `consulta_general`, `quiere_aplicar`, `pregunta_visado`,
   `hablar_con_humano`, `otro`.
3. `POST /api/whatsapp/classification`: guarda intención y confianza en el
   mensaje, rellena el país del lead si faltaba y marca `needsHuman` cuando la
   intención es `hablar_con_humano`, la confianza está por debajo de
   `CLASSIFIER_CONFIDENCE_THRESHOLD` o el clasificador falló.
4. Envío por WhatsApp y `POST /api/whatsapp/outbound`. Sin token de Meta, la
   respuesta solo se loguea.

El agente **no cambia la etapa del lead**: eso queda para un asesor
(human-in-the-loop). Sin clave de Anthropic se responde con un acuse fijo.

## Variables de entorno

| Variable | Descripción |
|---|---|
| `META_WHATSAPP_TOKEN`, `META_PHONE_NUMBER_ID` | Envío de mensajes. Vacíos en local = solo log. |
| `META_WEBHOOK_VERIFY_TOKEN`, `META_APP_SECRET` | Verificación y firma del webhook. |
| `CRM_API_URL`, `CRM_INTERNAL_API_KEY` | Acceso a la API interna del CRM. |
| `ANTHROPIC_API_KEY` | Activa el clasificador. |
| `CLAUDE_MODEL` | Por defecto `claude-opus-5`. |
| `CLASSIFIER_CONFIDENCE_THRESHOLD` | Por defecto `0.6`. |

## Limitaciones actuales

- Solo procesa mensajes de texto; imágenes, audios y documentos se ignoran.
- El clasificador responde a partir del historial de la conversación, sin base
  de conocimiento propia (RAG es el siguiente paso del roadmap).

# agent-service

Servicio Python (FastAPI) que recibe el webhook de Meta WhatsApp Cloud API,
registra cada mensaje como lead/mensaje en el CRM (`crm-web`) y responde por
WhatsApp. Corre como proceso independiente del CRM (ver `DOCS/01-arquitectura.md`).

## Correr en local

```bash
cd agent-service
python -m venv .venv
.venv/Scripts/activate        # Windows (en bash: source .venv/Scripts/activate)
pip install -r requirements.txt
cp .env.example .env          # ajustar claves; META_WHATSAPP_TOKEN puede quedar vacio
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

## Limitaciones actuales

- Solo procesa mensajes de texto; imágenes, audios y documentos se ignoran.
- La respuesta es un acuse fijo; la clasificación de intención con IA es el siguiente paso del roadmap.
- Si `META_WHATSAPP_TOKEN` está vacío, la respuesta se loguea en vez de enviarse (útil en local).

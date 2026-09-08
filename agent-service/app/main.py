import json
import logging

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.classifier import IntentClassifier
from app.config import get_settings
from app.crm import CRMClient
from app.handler import handle_inbound
from app.security import verify_signature
from app.whatsapp import WhatsAppClient, parse_inbound_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ISP CRM IA - Agent Service")


@app.on_event("startup")
def log_configuration() -> None:
    settings = get_settings()
    logger.info(
        "WhatsApp: %s | Clasificador IA: %s (%s)",
        "configurado" if settings.whatsapp_configured else "no configurado (solo log)",
        "activo" if settings.classifier_configured else "inactivo (acuse fijo)",
        settings.claude_model,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/webhook")
def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    verify_token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse:
    settings = get_settings()
    if mode == "subscribe" and verify_token == settings.meta_webhook_verify_token:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="verify token invalido")


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    settings = get_settings()
    body = await request.body()

    if not verify_signature(settings.meta_app_secret, body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=401, detail="firma invalida")

    messages = parse_inbound_messages(json.loads(body))
    if not messages:
        return {"status": "ignored"}

    crm = CRMClient(settings.crm_api_url, settings.crm_internal_api_key)
    whatsapp = (
        WhatsAppClient(
            settings.meta_whatsapp_token,
            settings.meta_phone_number_id,
            settings.meta_graph_api_version,
        )
        if settings.whatsapp_configured
        else None
    )
    classifier = (
        IntentClassifier(settings.anthropic_api_key, settings.claude_model)
        if settings.classifier_configured
        else None
    )

    # Meta exige responder 200 rapido; el procesamiento sigue en segundo plano.
    for message in messages:
        background_tasks.add_task(
            handle_inbound,
            message,
            crm,
            whatsapp,
            classifier,
            settings.classifier_confidence_threshold,
        )

    return {"status": "received", "messages": len(messages)}

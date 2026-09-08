import logging

import anthropic

from app.classifier import ClassificationUnavailable, IntentClassifier
from app.crm import CRMClient
from app.whatsapp import InboundMessage, WhatsAppClient

logger = logging.getLogger(__name__)


def build_reply(name: str | None, is_new: bool) -> str:
    greeting = f"Hola {name}" if name else "Hola"
    if is_new:
        return (
            f"{greeting}, gracias por escribirnos. Un asesor revisará tu consulta "
            "y te responderá en breve."
        )
    return f"{greeting}, recibimos tu mensaje. Te respondemos en breve."


async def handle_inbound(
    message: InboundMessage,
    crm: CRMClient,
    whatsapp: WhatsAppClient | None,
    classifier: IntentClassifier | None,
    confidence_threshold: float = 0.6,
) -> None:
    result = await crm.register_inbound(
        phone=message.phone,
        name=message.name,
        text=message.text,
        wa_message_id=message.message_id,
    )
    if result.get("duplicate"):
        logger.info("Mensaje %s ya registrado, se ignora el reintento", message.message_id)
        return

    reply = build_reply(message.name, result["isNew"])

    if classifier is not None:
        # El historial incluye el mensaje recien guardado; se pasa aparte como "ultimo mensaje".
        history = result.get("history", [])[:-1]
        try:
            classification = await classifier.classify(message, history)
        except (anthropic.APIError, ClassificationUnavailable) as error:
            logger.warning("Clasificador no disponible (%s); se marca para un asesor", error)
            await crm.register_classification(message_id=result["messageId"], needs_human=True)
        else:
            reply = classification.reply
            needs_human = (
                classification.intent == "hablar_con_humano"
                or classification.confidence < confidence_threshold
            )
            await crm.register_classification(
                message_id=result["messageId"],
                needs_human=needs_human,
                intent=classification.intent,
                confidence=classification.confidence,
                country_of_interest=classification.country_of_interest,
            )
            logger.info(
                "Lead %s: intent=%s confidence=%.2f needs_human=%s",
                result["leadId"], classification.intent, classification.confidence, needs_human,
            )

    if whatsapp is None:
        logger.info(
            "WhatsApp no configurado; respuesta para %s no enviada: %r", message.phone, reply
        )
        return

    sent_id = await whatsapp.send_text(message.wa_id, reply)
    await crm.register_outbound(lead_id=result["leadId"], text=reply, wa_message_id=sent_id)

import logging

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
    message: InboundMessage, crm: CRMClient, whatsapp: WhatsAppClient | None
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

    if whatsapp is None:
        logger.info(
            "WhatsApp no configurado; respuesta para %s no enviada: %r", message.phone, reply
        )
        return

    sent_id = await whatsapp.send_text(message.wa_id, reply)
    await crm.register_outbound(lead_id=result["leadId"], text=reply, wa_message_id=sent_id)

from dataclasses import dataclass

import httpx


@dataclass
class InboundMessage:
    wa_id: str
    name: str | None
    text: str
    message_id: str

    @property
    def phone(self) -> str:
        return f"+{self.wa_id}"


def parse_inbound_messages(payload: dict) -> list[InboundMessage]:
    """Extrae los mensajes de texto de un webhook de Cloud API.

    Ignora eventos de estado (entregado/leido) y, por ahora, mensajes que no
    son de texto (imagen, audio, documento...).
    """
    messages: list[InboundMessage] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {
                contact.get("wa_id"): contact.get("profile", {}).get("name")
                for contact in value.get("contacts", [])
            }
            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue
                messages.append(
                    InboundMessage(
                        wa_id=message["from"],
                        name=names.get(message["from"]),
                        text=message["text"]["body"],
                        message_id=message["id"],
                    )
                )
    return messages


class WhatsAppClient:
    def __init__(self, token: str, phone_number_id: str, api_version: str):
        self._token = token
        self._url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"

    async def send_text(self, to_wa_id: str, text: str) -> str:
        """Envia un mensaje de texto y devuelve el id que asigna Meta."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_wa_id,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self._url, json=payload, headers={"Authorization": f"Bearer {self._token}"}
            )
            response.raise_for_status()
            return response.json()["messages"][0]["id"]

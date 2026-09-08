import httpx


class CRMClient:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {"x-internal-api-key": api_key}

    async def register_inbound(
        self, phone: str, name: str | None, text: str, wa_message_id: str
    ) -> dict:
        return await self._post(
            "/api/whatsapp/inbound",
            {"phone": phone, "name": name, "text": text, "waMessageId": wa_message_id},
        )

    async def register_classification(
        self,
        message_id: str,
        needs_human: bool,
        intent: str | None = None,
        confidence: float | None = None,
        country_of_interest: str | None = None,
    ) -> dict:
        return await self._post(
            "/api/whatsapp/classification",
            {
                "messageId": message_id,
                "needsHuman": needs_human,
                "intent": intent,
                "confidence": confidence,
                "countryOfInterest": country_of_interest,
            },
        )

    async def register_outbound(self, lead_id: str, text: str, wa_message_id: str) -> dict:
        return await self._post(
            "/api/whatsapp/outbound",
            {"leadId": lead_id, "text": text, "waMessageId": wa_message_id},
        )

    async def _post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self._base_url}{path}", json=payload, headers=self._headers
            )
            response.raise_for_status()
            return response.json()

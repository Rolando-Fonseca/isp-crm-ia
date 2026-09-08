import asyncio

import pytest

from app.classifier import Classification, ClassificationUnavailable
from app.handler import handle_inbound
from app.whatsapp import InboundMessage

MESSAGE = InboundMessage(
    wa_id="5491155550199", name="Ana", text="Quiero hablar con alguien", message_id="wamid.1"
)


class FakeCRM:
    def __init__(self, is_new: bool = True):
        self.is_new = is_new
        self.classifications = []
        self.outbound = []

    async def register_inbound(self, phone, name, text, wa_message_id):
        return {
            "leadId": "lead-1",
            "messageId": "msg-1",
            "stage": "ENQUIRY",
            "isNew": self.is_new,
            "countryOfInterest": None,
            "history": [{"direction": "INBOUND", "body": text}],
        }

    async def register_classification(self, **kwargs):
        self.classifications.append(kwargs)
        return {"ok": True}

    async def register_outbound(self, lead_id, text, wa_message_id):
        self.outbound.append(text)
        return {"ok": True}


class FakeWhatsApp:
    def __init__(self):
        self.sent = []

    async def send_text(self, to_wa_id, text):
        self.sent.append((to_wa_id, text))
        return "wamid.sent"


class FakeClassifier:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    async def classify(self, message, history):
        self.calls.append((message, history))
        if self.error:
            raise self.error
        return self.result


def run(coro):
    return asyncio.run(coro)


def test_without_classifier_uses_fixed_reply():
    crm, whatsapp = FakeCRM(is_new=True), FakeWhatsApp()
    run(handle_inbound(MESSAGE, crm, whatsapp, classifier=None))
    assert crm.classifications == []
    assert whatsapp.sent[0][1].startswith("Hola Ana, gracias por escribirnos")
    assert crm.outbound == [whatsapp.sent[0][1]]


def test_classifier_reply_is_sent_and_recorded():
    classification = Classification(
        intent="hablar_con_humano",
        confidence=0.95,
        country_of_interest="Canadá",
        reply="Claro Ana, un asesor te escribe en breve.",
    )
    classifier = FakeClassifier(result=classification)
    crm, whatsapp = FakeCRM(), FakeWhatsApp()

    run(handle_inbound(MESSAGE, crm, whatsapp, classifier))

    assert whatsapp.sent == [("5491155550199", "Claro Ana, un asesor te escribe en breve.")]
    assert crm.classifications == [
        {
            "message_id": "msg-1",
            "needs_human": True,
            "intent": "hablar_con_humano",
            "confidence": 0.95,
            "country_of_interest": "Canadá",
        }
    ]
    # El mensaje actual no se repite dentro del historial que ve el modelo.
    assert classifier.calls[0][1] == []


def test_low_confidence_flags_human():
    classification = Classification(
        intent="consulta_general", confidence=0.3, country_of_interest=None, reply="Hola."
    )
    crm = FakeCRM()
    run(handle_inbound(MESSAGE, crm, None, FakeClassifier(result=classification), 0.6))
    assert crm.classifications[0]["needs_human"] is True


@pytest.mark.parametrize("error", [ClassificationUnavailable("refusal")])
def test_classifier_failure_falls_back_and_flags_human(error):
    crm, whatsapp = FakeCRM(is_new=False), FakeWhatsApp()
    run(handle_inbound(MESSAGE, crm, whatsapp, FakeClassifier(error=error)))
    assert crm.classifications == [{"message_id": "msg-1", "needs_human": True}]
    assert whatsapp.sent[0][1] == "Hola Ana, recibimos tu mensaje. Te respondemos en breve."

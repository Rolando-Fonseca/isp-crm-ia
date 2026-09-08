from app.whatsapp import parse_inbound_messages


def text_payload(wa_id: str = "5491155550101", name: str = "Camila", text: str = "Hola") -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "1555", "phone_number_id": "PNID"},
                            "contacts": [{"profile": {"name": name}, "wa_id": wa_id}],
                            "messages": [
                                {
                                    "from": wa_id,
                                    "id": "wamid.TEST1",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def test_parses_text_message():
    messages = parse_inbound_messages(text_payload())
    assert len(messages) == 1
    message = messages[0]
    assert message.wa_id == "5491155550101"
    assert message.phone == "+5491155550101"
    assert message.name == "Camila"
    assert message.text == "Hola"
    assert message.message_id == "wamid.TEST1"


def test_ignores_status_updates():
    payload = text_payload()
    value = payload["entry"][0]["changes"][0]["value"]
    del value["messages"]
    value["statuses"] = [{"id": "wamid.TEST1", "status": "delivered"}]
    assert parse_inbound_messages(payload) == []


def test_ignores_non_text_messages():
    payload = text_payload()
    message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
    message["type"] = "image"
    del message["text"]
    assert parse_inbound_messages(payload) == []

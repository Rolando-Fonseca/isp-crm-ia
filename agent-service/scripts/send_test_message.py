"""Simula un webhook de WhatsApp Cloud API contra el servicio local.

Construye el mismo payload que envia Meta, lo firma con META_APP_SECRET del .env
y lo manda a /webhook. Sirve para probar el flujo completo sin cuenta de Meta.

    python scripts/send_test_message.py --phone 5491155550199 --name "Ana" --text "Hola"
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402
from app.security import compute_signature  # noqa: E402


def build_payload(wa_id: str, name: str, text: str) -> dict:
    now = str(int(time.time()))
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_TEST",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "15550000000", "phone_number_id": "PNID_TEST"},
                            "contacts": [{"profile": {"name": name}, "wa_id": wa_id}],
                            "messages": [
                                {
                                    "from": wa_id,
                                    "id": f"wamid.LOCAL.{wa_id}.{now}",
                                    "timestamp": now,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8002/webhook")
    parser.add_argument("--phone", required=True, help="wa_id sin '+', ej: 5491155550199")
    parser.add_argument("--name", default="Lead de prueba")
    parser.add_argument("--text", default="Hola, quiero informacion")
    args = parser.parse_args()

    body = json.dumps(build_payload(args.phone, args.name, args.text)).encode()
    signature = compute_signature(get_settings().meta_app_secret, body)

    response = httpx.post(
        args.url,
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
    )
    print(response.status_code, response.text)


if __name__ == "__main__":
    main()

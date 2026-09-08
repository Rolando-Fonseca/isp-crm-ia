import json

import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import get_settings
from app.security import compute_signature
from tests.test_whatsapp import text_payload

APP_SECRET = "test-app-secret"
VERIFY_TOKEN = "test-verify-token"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("META_APP_SECRET", APP_SECRET)
    monkeypatch.setenv("META_WEBHOOK_VERIFY_TOKEN", VERIFY_TOKEN)
    monkeypatch.setenv("CRM_INTERNAL_API_KEY", "test-key")
    get_settings.cache_clear()
    yield TestClient(main.app)
    get_settings.cache_clear()


@pytest.fixture
def handled(monkeypatch):
    calls = []

    async def fake_handle_inbound(message, *args):
        calls.append(message)

    monkeypatch.setattr(main, "handle_inbound", fake_handle_inbound)
    return calls


def test_verification_returns_challenge(client):
    response = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": VERIFY_TOKEN, "hub.challenge": "12345"},
    )
    assert response.status_code == 200
    assert response.text == "12345"


def test_verification_rejects_wrong_token(client):
    response = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "12345"},
    )
    assert response.status_code == 403


def test_rejects_invalid_signature(client, handled):
    body = json.dumps(text_payload()).encode()
    response = client.post(
        "/webhook", content=body, headers={"X-Hub-Signature-256": "sha256=deadbeef"}
    )
    assert response.status_code == 401
    assert handled == []


def test_accepts_signed_message_and_dispatches(client, handled):
    body = json.dumps(text_payload(text="Quiero estudiar en España")).encode()
    response = client.post(
        "/webhook",
        content=body,
        headers={"X-Hub-Signature-256": compute_signature(APP_SECRET, body)},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "received", "messages": 1}
    assert len(handled) == 1
    assert handled[0].text == "Quiero estudiar en España"

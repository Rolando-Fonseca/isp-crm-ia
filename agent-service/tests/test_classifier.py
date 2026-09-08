from app.classifier import build_user_prompt
from app.whatsapp import InboundMessage


def test_prompt_includes_history_and_last_message():
    message = InboundMessage(
        wa_id="5491155550199", name="Ana", text="¿Y para Canadá?", message_id="wamid.2"
    )
    history = [
        {"direction": "INBOUND", "body": "Hola, quiero estudiar afuera"},
        {"direction": "OUTBOUND", "body": "Hola Ana, ¿qué país te interesa?"},
    ]
    prompt = build_user_prompt(message, history)
    assert "Estudiante: Hola, quiero estudiar afuera" in prompt
    assert "Agencia: Hola Ana, ¿qué país te interesa?" in prompt
    assert prompt.endswith("Último mensaje del estudiante (Ana):\n¿Y para Canadá?")


def test_prompt_without_history():
    message = InboundMessage(wa_id="1", name=None, text="Hola", message_id="wamid.3")
    prompt = build_user_prompt(message, [])
    assert "(sin mensajes anteriores)" in prompt
    assert "(sin nombre)" in prompt

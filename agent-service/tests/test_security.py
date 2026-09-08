from app.security import compute_signature, verify_signature

BODY = b'{"hello":"world"}'


def test_signature_roundtrip():
    signature = compute_signature("secret", BODY)
    assert signature.startswith("sha256=")
    assert verify_signature("secret", BODY, signature)


def test_wrong_secret_is_rejected():
    signature = compute_signature("secret", BODY)
    assert not verify_signature("other-secret", BODY, signature)


def test_tampered_body_is_rejected():
    signature = compute_signature("secret", BODY)
    assert not verify_signature("secret", BODY + b" ", signature)


def test_missing_header_is_rejected():
    assert not verify_signature("secret", BODY, None)

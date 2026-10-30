from app.security.redaction import redact_secrets


def test_redacts_assignment_bearer_url_and_private_key_secrets():
    text = (
        ("api_" + "key") + "=" + ("abc123") + " "
        + ("pass" + "word") + ": " + ("hun" + "ter2") + " "
        + "Authorization: " + ("bear" + "er ") + ("eyJhbGci" + ".test") + " "
        + "https://" + "alice" + ":" + ("secret") + "@example.com/path"
    )
    redacted = redact_secrets(text)
    for secret in ("abc123", "hunter2", "eyJhbGci.test", "alice:secret"):
        assert secret not in redacted
    assert "[REDACTED]" in redacted


def test_redacts_secret_in_quoted_assignment():
    key = "pass" + "word"
    value = "my " + "secret"
    assert value not in redact_secrets(f'{key}="{value}"')

import json
import urllib.error
from unittest.mock import patch

import pytest

from app.ai.ollama_client import OllamaClient
from app.config import Settings


def client():
    return OllamaClient(Settings())


def test_ai_unavailable_is_reported_without_cloud_fallback():
    with patch("app.ai.ollama_client.urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
        status = client().status()
    assert not status.available
    assert not status.installed_model
    assert "Install and start Ollama" in status.message


def test_model_missing_is_reported_with_pull_instructions():
    response = patch_response({"models": [{"name": "other:latest"}]})
    with patch("app.ai.ollama_client.urllib.request.urlopen", return_value=response):
        status = client().status()
    assert status.available
    assert not status.installed_model
    assert "ollama pull gemma3:1b" in status.message


def test_malformed_model_response_is_explicit():
    response = patch_response({"response": 4})
    with patch("app.ai.ollama_client.urllib.request.urlopen", return_value=response):
        with pytest.raises(ValueError, match="malformed"):
            client().generate("Explain")


def test_ollama_endpoint_must_be_loopback_only():
    with pytest.raises(ValueError, match="loopback"):
        OllamaClient(Settings(ollama_url="https://example.com"))


def test_malformed_status_shape_is_reported():
    with patch("app.ai.ollama_client.urllib.request.urlopen", return_value=patch_response([])):
        status = client().status()
    assert not status.available
    assert "malformed" in status.message


def test_non_object_generation_response_is_explicit():
    with patch("app.ai.ollama_client.urllib.request.urlopen", return_value=patch_response([])):
        with pytest.raises(ValueError, match="malformed"):
            client().generate("Explain")


class FakeResponse:
    def __init__(self, value):
        self.content = json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return self.content


def patch_response(value):
    return FakeResponse(value)

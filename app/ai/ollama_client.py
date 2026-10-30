from __future__ import annotations

import json
import ipaddress
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit

from app.config import Settings


@dataclass(frozen=True)
class AIStatus:
    available: bool
    installed_model: bool
    model: str
    message: str


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        endpoint = urlsplit(settings.ollama_url)
        try:
            is_loopback = endpoint.hostname == "localhost" or (
                endpoint.hostname is not None and ipaddress.ip_address(endpoint.hostname).is_loopback
            )
        except ValueError:
            is_loopback = False
        if (
            endpoint.scheme not in {"http", "https"}
            or not is_loopback
            or endpoint.username is not None
            or endpoint.password is not None
            or endpoint.path not in {"", "/"}
            or endpoint.query
            or endpoint.fragment
        ):
            raise ValueError("Ollama must use a credential-free loopback URL such as http://127.0.0.1:11434.")

    def status(self) -> AIStatus:
        try:
            with urllib.request.urlopen(
                f"{self.settings.ollama_url}/api/tags", timeout=2
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
            if not isinstance(body, dict) or not isinstance(body.get("models"), list):
                return AIStatus(False, False, self.settings.model, "Ollama returned a malformed model-status response.")
            installed = any(
                item.get("name") == self.settings.model
                or item.get("model") == self.settings.model
                for item in body["models"]
                if isinstance(item, dict)
            )
            message = (
                "Local model is ready."
                if installed
                else f"Ollama is running, but {self.settings.model} is not downloaded. Run: ollama pull {self.settings.model}"
            )
            return AIStatus(True, installed, self.settings.model, message)
        except json.JSONDecodeError:
            return AIStatus(False, False, self.settings.model, "Ollama returned malformed JSON for model status.")
        except (urllib.error.URLError, TimeoutError, OSError, UnicodeDecodeError):
            return AIStatus(
                False,
                False,
                self.settings.model,
                f"Ollama is unavailable at {self.settings.ollama_url}. Install and start Ollama to enable local AI.",
            )

    def generate(self, prompt: str) -> str:
        payload = json.dumps(
            {"model": self.settings.model, "prompt": prompt, "stream": False},
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.settings.ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.request_timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError("Ollama returned a malformed response.")
            text = result.get("response")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Ollama returned an empty or malformed response.")
            return text.strip()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Local AI request failed: {exc}") from exc

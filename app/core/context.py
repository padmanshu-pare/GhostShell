from __future__ import annotations

from dataclasses import asdict, dataclass

from app.security.redaction import redact_secrets


@dataclass(frozen=True)
class InvestigationContext:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    risk_level: str
    working_directory: str
    recent_context: tuple[str, ...] = ()

    def safe_payload(self) -> dict[str, object]:
        data = asdict(self)
        for key in ("command", "stdout", "stderr", "working_directory"):
            data[key] = redact_secrets(str(data[key]))[:16_000]
        data["recent_context"] = [redact_secrets(entry)[:1_000] for entry in self.recent_context[-10:]]
        return data

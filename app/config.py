from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    ollama_url: str = "http://127.0.0.1:11434"
    model: str = "gemma3:1b"
    request_timeout: float = 25.0
    command_timeout: float = 15.0
    output_limit: int = 64_000
    history_limit: int = 30
    database_path: Path = Path.home() / ".ghostshell" / "ghostshell.db"
    allowed_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    @classmethod
    def from_env(cls) -> Settings:
        origins = os.getenv("GHOSTSHELL_ALLOWED_ORIGINS")
        return cls(
            ollama_url=os.getenv("GHOSTSHELL_OLLAMA_URL", cls.ollama_url).rstrip("/"),
            model=os.getenv("GHOSTSHELL_MODEL", cls.model),
            request_timeout=float(os.getenv("GHOSTSHELL_REQUEST_TIMEOUT", cls.request_timeout)),
            command_timeout=float(os.getenv("GHOSTSHELL_COMMAND_TIMEOUT", cls.command_timeout)),
            output_limit=int(os.getenv("GHOSTSHELL_OUTPUT_LIMIT", cls.output_limit)),
            history_limit=int(os.getenv("GHOSTSHELL_HISTORY_LIMIT", cls.history_limit)),
            database_path=Path(os.getenv("GHOSTSHELL_DATABASE", cls.database_path)),
            allowed_origins=tuple(item.strip() for item in origins.split(",") if item.strip())
            if origins
            else cls.allowed_origins,
        )

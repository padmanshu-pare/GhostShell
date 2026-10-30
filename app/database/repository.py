from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from app.database.db import connect
from app.security.redaction import redact_secrets


class HistoryRepository:
    def __init__(self, path: Path, retention: int = 30) -> None:
        self.path = path
        self.retention = max(1, retention)

    def create_session(self, personality: str = "guardian") -> str:
        session_id = str(uuid.uuid4())
        with connect(self.path) as db:
            db.execute(
                "INSERT INTO sessions (id, personality) VALUES (?, ?)",
                (session_id, personality),
            )
        return session_id

    def set_personality(self, session_id: str, personality: str) -> None:
        with connect(self.path) as db:
            db.execute(
                "UPDATE sessions SET personality = ? WHERE id = ?",
                (personality, session_id),
            )

    def add(
        self,
        session_id: str,
        command: str,
        exit_code: int | None,
        risk_level: str,
        summary: str = "",
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        safe = tuple(redact_secrets(value) for value in (command, summary, stdout, stderr))
        with connect(self.path) as db:
            db.execute(
                """INSERT INTO history
                   (session_id, command, exit_code, risk_level, summary, stdout, stderr)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, safe[0][:2_000], exit_code, risk_level, safe[1][:4_000], safe[2][:16_000], safe[3][:16_000]),
            )
            db.execute(
                """DELETE FROM history WHERE id NOT IN
                   (SELECT id FROM history ORDER BY id DESC LIMIT ?)""",
                (self.retention,),
            )

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            rows = db.execute(
                """SELECT command, exit_code, risk_level, summary, stdout, stderr, created_at
                   FROM history ORDER BY id DESC LIMIT ?""",
                (max(1, min(limit, 200)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def clear(self) -> None:
        with connect(self.path) as db:
            db.execute("DELETE FROM history")

    def recent_summaries(self, limit: int = 10) -> tuple[str, ...]:
        with connect(self.path) as db:
            rows = db.execute(
                "SELECT summary FROM history WHERE summary != '' ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return tuple(str(row["summary"]) for row in reversed(rows))

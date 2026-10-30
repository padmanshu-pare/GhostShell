from __future__ import annotations

import secrets
from dataclasses import dataclass
from pathlib import Path

from app.security.command_policy import RiskLevel


@dataclass(frozen=True)
class Approval:
    token: str
    command: str
    working_directory: Path
    context: str


class ApprovalGate:
    def __init__(self) -> None:
        self._pending: dict[str, Approval] = {}

    def request(self, command: str, working_directory: Path, context: str = "local") -> Approval:
        approval = Approval(secrets.token_urlsafe(24), command, working_directory.resolve(), context)
        self._pending[approval.token] = approval
        return approval

    def consume(
        self,
        token: str | None,
        command: str,
        working_directory: Path,
        context: str = "local",
        risk: RiskLevel = RiskLevel.CAUTION,
    ) -> bool:
        if token is None:
            return False
        approval = self._pending.pop(token, None)
        if approval is None or risk is not RiskLevel.CAUTION:
            return False
        return (
            approval.command == command
            and approval.working_directory == working_directory.resolve()
            and approval.context == context
        )

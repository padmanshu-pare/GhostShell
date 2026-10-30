from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.context import InvestigationContext


@dataclass(frozen=True)
class Finding:
    summary: str
    cause: str
    diagnostic: str
    confidence: str = "Likely"


_SIGNATURES = (
    (
        re.compile(r"EADDRINUSE|address already in use", re.IGNORECASE),
        Finding(
            "A local network port is already in use.",
            "Another development server or application may be listening on that port.",
            "Get-NetTCPConnection -LocalPort 3000",
        ),
    ),
    (
        re.compile(r"Cannot find module ['\"]vite['\"]|MODULE_NOT_FOUND", re.IGNORECASE),
        Finding(
            "Node.js could not find a required package.",
            "Project dependencies may not be installed, or the package is missing from package.json.",
            "Inspect package.json and run npm install after reviewing the dependency changes.",
        ),
    ),
    (
        re.compile(r"command not found|is not recognized as the name|Could not start command", re.IGNORECASE),
        Finding(
            "The requested executable was not found.",
            "It may not be installed, or its installation directory may not be on PATH.",
            "Check the tool's installation and version using its official local command.",
        ),
    ),
    (
        re.compile(r"Permission denied|Access is denied", re.IGNORECASE),
        Finding(
            "The operation was denied by the operating system.",
            "The current user may not have permission to access the target.",
            "Check the target path and its permissions; avoid elevating privileges unless necessary.",
        ),
    ),
)


def investigate(context: InvestigationContext) -> Finding:
    evidence = f"{context.stderr}\n{context.stdout}"
    for signature, finding in _SIGNATURES:
        if signature.search(evidence):
            return finding
    if context.exit_code != 0:
        return Finding(
            "The command exited with a non-zero status.",
            "The available output does not match a known error signature, so the exact cause is unconfirmed.",
            "Review the complete error output and rerun a focused, read-only diagnostic.",
            confidence="Unconfirmed",
        )
    return Finding("The command completed successfully.", "No failure was observed.", "No diagnostic needed.", "Confirmed")

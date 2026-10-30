from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGEROUS = "DANGEROUS"


@dataclass(frozen=True)
class RiskAssessment:
    level: RiskLevel
    reason: str
    suggested_alternative: str | None = None


_CHAINING = re.compile(r"(?:&&|\|\||[;&|<>])")
_OBVIOUS_DESTRUCTION = re.compile(
    r"(?i)(?:\brm\b.*(?:-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)|"
    r"\b(?:format|diskpart)\b|\bdel\b.*(?:/s|/q)|"
    r"\bremove-item\b.*(?:-recurse|-force).*(?:[A-Za-z]:\\?$|\\\*|\*\\)|"
    r"\b(?:iex|invoke-expression)\b|(?:^|\s)-(?:e|en|enc|enco|encod|encoded|encodedcommand)(?:\s|$)|"
    r"\b(?:iwr|irm|curl|wget)\b.*\|\s*(?:iex|invoke-expression))"
)
_DESTRUCTIVE = re.compile(
    r"(?i)(?:\b(?:rm|del|erase|rmdir|rd|remove-item)\b|\b(?:format|diskpart)\b)"
)
_CAUTION = re.compile(
    r"(?i)(?:\b(?:npm|pip)\s+install\b|\bgit\s+(?:reset|clean)\b|"
    r"\b(?:taskkill|stop-process)\b|\b(?:pytest|npm\s+run)\b)"
)
_SAFE_COMMANDS = {
    ("pwd",),
    ("ls",),
    ("dir",),
    ("git", "status"),
    ("git", "log"),
    ("git", "branch"),
    ("node", "--version"),
    ("node", "-v"),
    ("npm", "--version"),
    ("npm", "-v"),
    ("python", "--version"),
    ("python", "-v"),
    ("pip", "--version"),
    ("pip", "-v"),
}
_SUPPORTED = {
    "git status",
    "git status --short",
    "git log",
    "git log --oneline",
    "git branch",
    "node --version",
    "node -v",
    "npm --version",
    "npm -v",
    "python --version",
    "python -v",
    "pip --version",
    "pip -v",
    "npm run dev",
    "npm install",
    "pip install",
    "pytest",
    "pytest --version",
}


def tokenize(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return []


def assess_command(command: str) -> RiskAssessment:
    normalized = command.strip()
    if not normalized:
        return RiskAssessment(RiskLevel.DANGEROUS, "An empty command cannot be executed.")
    if _OBVIOUS_DESTRUCTION.search(normalized):
        return RiskAssessment(
            RiskLevel.DANGEROUS,
            "This command can recursively delete data, alter a disk, execute encoded code, or run a downloaded script.",
            "Inspect the target and use a narrowly scoped, explicit action instead.",
        )
    if _CHAINING.search(normalized):
        return RiskAssessment(
            RiskLevel.DANGEROUS,
            "Shell chaining, redirection, and pipelines are not supported by the controlled runner.",
            "Run one supported command at a time.",
        )

    tokens = tokenize(normalized)
    if not tokens:
        return RiskAssessment(RiskLevel.DANGEROUS, "The command could not be parsed safely.")
    lowered = tuple(token.casefold() for token in tokens)
    executable = lowered[0].rsplit("\\", 1)[-1].removesuffix(".exe")
    canonical = (executable, *lowered[1:])
    if canonical in _SAFE_COMMANDS:
        return RiskAssessment(RiskLevel.SAFE, "Recognized read-only command from the supported command set.")
    if lowered[0] in {"rm", "del", "erase", "rmdir", "rd", "remove-item", "format", "diskpart"}:
        return RiskAssessment(
            RiskLevel.DANGEROUS,
            "File deletion or disk-management commands are blocked by GhostGuard.",
        )
    if _DESTRUCTIVE.search(normalized) and not re.search(
        r"(?i)^(?:rm\s+-[a-z]*r[a-z]*f\s+\S+|remove-item\s+[^*]+\s+-recurse)$", normalized
    ):
        return RiskAssessment(
            RiskLevel.DANGEROUS,
            "Process termination and broad destructive operations are blocked by default.",
        )
    if _CAUTION.search(normalized):
        return RiskAssessment(
            RiskLevel.CAUTION,
            "This command can modify project files, install packages, run project code, or affect processes.",
        )

    if normalized.casefold() in _SUPPORTED:
        return RiskAssessment(RiskLevel.SAFE, "Recognized command from the supported command set.")
    return RiskAssessment(
        RiskLevel.CAUTION,
        "This command is not in the read-only safe set and requires review; unsupported commands still cannot run.",
    )


def is_supported_command(command: str) -> bool:
    normalized = " ".join(tokenize(command.strip())).casefold()
    if normalized in _SUPPORTED:
        return True
    tokens = tokenize(command.strip())
    return len(tokens) == 1 and tokens[0].casefold() in {"pytest"}

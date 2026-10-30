from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.config import Settings
from app.database.repository import HistoryRepository
from app.runner import CommandDenied, ControlledRunner
from app.security.approval import ApprovalGate
from app.security.command_policy import RiskLevel, assess_command, is_supported_command, tokenize

PERSONALITIES = {"ancient", "cursed", "guardian"}


class GhostTerminal:
    def __init__(self, settings: Settings, console: Console | None = None) -> None:
        self.settings = settings
        self.console = console or Console()
        self.approvals = ApprovalGate()
        self.runner = ControlledRunner(settings, self.approvals)
        self.history = HistoryRepository(settings.database_path, settings.history_limit)
        self.session_id = self.history.create_session()
        self.cwd = Path.cwd().resolve()
        self.personality = "guardian"

    def banner(self, ai_message: str) -> None:
        self.console.print(
            Panel(
                "[bold #7CFF9B]G H O S T S H E L L[/bold #7CFF9B]\n\n"
                "[white]YOUR TERMINAL HAS AWAKENED[/white]\n\n"
                f"[#94A3B8]AI CORE    : GEMMA 3 ({self.settings.model})\n"
                f"INFERENCE  : LOCAL\nGUARD      : ACTIVE\n"
                f"PRIVACY    : PROTECTED[/#94A3B8]\n\n"
                f"[dim]{ai_message}[/dim]",
                border_style="#263241",
                title="[bold #9D7BFF]GHOSTSHELL[/bold #9D7BFF]",
            )
        )

    def handle(self, command: str) -> bool:
        tokens = tokenize(command)
        if not tokens:
            self.console.print("[yellow]Enter a command, or type help.[/yellow]")
            return True
        verb = tokens[0].casefold()
        if verb in {"exit", "quit"}:
            return False
        if verb in {"help", "?"}:
            self._help()
            return True
        if verb in {"clear", "cls"} and len(tokens) == 1:
            self.console.clear()
            return True
        if verb == "cd":
            if len(tokens) > 2:
                self.console.print("[yellow]Usage: cd [path][/yellow]")
                return True
            self._change_directory(tokens[1] if len(tokens) == 2 else "")
            return True
        if verb == "personality":
            self._personality(tokens[1] if len(tokens) == 2 else "")
            return True
        if verb == "history":
            for entry in self.history.history(12):
                self.console.print(
                    f"[dim]{entry['created_at']}[/dim] [{entry['risk_level']}] "
                    f"{entry['command']} [exit {entry['exit_code']}]"
                )
            return True
        if verb == "clear-history":
            self.history.clear()
            self.console.print("[#7CFF9B]Local history cleared.[/#7CFF9B]")
            return True
        if verb == "pwd" and len(tokens) == 1:
            self.console.print(str(self.cwd))
            return True
        if verb in {"ls", "dir"} and len(tokens) == 1:
            self._list_directory()
            return True
        if verb in {"ls", "dir"}:
            self.console.print("[yellow]GhostShell lists the current directory only. Use cd to navigate first.[/yellow]")
            return True
        self._execute(command)
        return True

    def _execute(self, command: str) -> None:
        risk = assess_command(command)
        if risk.level is RiskLevel.DANGEROUS:
            self.console.print(
                Panel(
                    f"[bold #FF4D5A]BLOCKED — {risk.reason}[/bold #FF4D5A]\n"
                    f"{risk.suggested_alternative or 'No override is available for dangerous commands.'}",
                    title="GhostGuard",
                    border_style="#FF4D5A",
                )
            )
            self.history.add(self.session_id, command, None, risk.level.value, risk.reason)
            return

        if not is_supported_command(command):
            message = "This command is not supported by GhostShell's controlled runner."
            self.console.print(f"[yellow]{message}[/yellow]")
            self.history.add(self.session_id, command, None, risk.level.value, message)
            return

        approval_token = None
        if risk.level is RiskLevel.CAUTION:
            approval = self.approvals.request(command, self.cwd)
            self.console.print(
                Panel(
                    f"[bold #9D7BFF]THE GHOST IS UNCERTAIN[/bold #9D7BFF]\n\n"
                    f"Command: {command}\nRisk: CAUTION\nPotential impact: {risk.reason}\n\n"
                    "[1] Approve once  [2] Deny  [3] Inspect command",
                    border_style="#9D7BFF",
                )
            )
            choice = input("Choice: ").strip()
            if choice == "3":
                self.console.print(f"Exact command: {command}\nDirectory: {self.cwd}")
                choice = input("Approve this exact command once? [y/N]: ").strip().casefold()
            if choice not in {"1", "y", "yes"}:
                self.history.add(self.session_id, command, None, risk.level.value, "Approval denied.")
                self.console.print("[yellow]Command denied. Nothing was executed.[/yellow]")
                return
            approval_token = approval.token

        try:
            result = self.runner.execute(command, self.cwd, approval_token)
        except CommandDenied as exc:
            self.console.print(f"[bold #FF4D5A]Blocked:[/bold #FF4D5A] {exc}")
            self.history.add(self.session_id, command, None, risk.level.value, str(exc))
            return

        output = result.stdout + result.stderr
        if output:
            self.console.print(output.rstrip())
        if result.output_truncated:
            self.console.print("[dim]Output was truncated to the configured size limit.[/dim]")
        summary = ""
        if result.exit_code != 0:
            from app.ai.gemma import GemmaInvestigator
            from app.ai.ollama_client import OllamaClient
            from app.core.context import InvestigationContext
            from app.core.orchestrator import explain_failure

            context = InvestigationContext(
                command,
                result.exit_code,
                result.stdout,
                result.stderr,
                result.risk.level.value,
                str(self.cwd),
                self.history.recent_summaries(),
            )
            finding, ai_text = explain_failure(
                context,
                self.personality,
                GemmaInvestigator(OllamaClient(self.settings)),
                OllamaClient(self.settings),
            )
            summary = finding.summary
            self.console.print(
                Panel(
                    f"[bold #7CFF9B]👻 {finding.summary}[/bold #7CFF9B]\n\n"
                    f"[white]Observation:[/white] {finding.cause}\n"
                    f"[white]Diagnostic:[/white] {finding.diagnostic}\n"
                    f"[dim]Confidence: {finding.confidence}[/dim]"
                    + (f"\n\n[white]Gemma:[/white]\n{ai_text}" if ai_text else ""),
                    title="Paranormal Investigator",
                    border_style="#7CFF9B",
                )
            )
        self.history.add(
            self.session_id, command, result.exit_code, result.risk.level.value,
            summary, result.stdout, result.stderr,
        )

    def _change_directory(self, target: str) -> None:
        path = (self.cwd / target).resolve() if target else Path.home()
        if not path.is_dir():
            self.console.print(f"[yellow]Not a directory: {path}[/yellow]")
            return
        self.cwd = path

    def _personality(self, name: str) -> None:
        if name not in PERSONALITIES:
            self.console.print("Choose: ancient, cursed, or guardian.")
            return
        self.personality = name
        self.history.set_personality(self.session_id, name)
        self.console.print(f"[#9D7BFF]Ghost personality: {name}[/#9D7BFF]")

    def _list_directory(self) -> None:
        try:
            for item in sorted(self.cwd.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.casefold())):
                suffix = os.sep if item.is_dir() else ""
                self.console.print(f"{item.name}{suffix}")
        except OSError as exc:
            self.console.print(f"[yellow]Could not list this directory: {exc}[/yellow]")

    def _help(self) -> None:
        self.console.print(
            Text(
                "Built-ins: pwd, ls, dir, cd <path>, clear, help, history, clear-history, "
                "personality <ancient|cursed|guardian>, exit\n"
                "Controlled commands: git status/log/branch; node/npm/python/pip --version; "
                "npm run dev; npm install; pip install; pytest.\n"
                "Unknown commands, shell chaining, and unrestricted PowerShell/Bash are not supported.",
                style="#94A3B8",
            )
        )

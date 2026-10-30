from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock, Thread
from typing import BinaryIO

from app.config import Settings
from app.security.approval import ApprovalGate
from app.security.command_policy import RiskAssessment, RiskLevel, assess_command, is_supported_command, tokenize


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    risk: RiskAssessment
    timed_out: bool = False
    output_truncated: bool = False


@dataclass
class CapturedStream:
    data: bytearray = field(default_factory=bytearray)
    truncated: bool = False
    lock: Lock = field(default_factory=Lock)


class CommandDenied(RuntimeError):
    pass


class ControlledRunner:
    def __init__(self, settings: Settings, approvals: ApprovalGate | None = None) -> None:
        self.settings = settings
        self.approvals = approvals or ApprovalGate()

    def execute(
        self,
        command: str,
        working_directory: Path,
        approval_token: str | None = None,
        context: str = "local",
    ) -> CommandResult:
        risk = assess_command(command)
        if risk.level is RiskLevel.DANGEROUS:
            raise CommandDenied(risk.reason)
        if risk.level is RiskLevel.CAUTION and not self.approvals.consume(
            approval_token, command, working_directory, context, risk.level
        ):
            raise CommandDenied("This command needs a fresh, exact-command approval.")
        if not is_supported_command(command):
            raise CommandDenied("This command is not supported by GhostShell's controlled runner.")

        try:
            cwd = working_directory.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise CommandDenied(f"The working directory is no longer available: {exc}") from exc
        if not cwd.is_dir():
            raise CommandDenied("The working directory must be an existing directory.")
        args = tokenize(command)
        if not args:
            raise CommandDenied("The command could not be parsed.")
        executable = args[0].casefold()
        if executable == "npm":
            npm_path = shutil.which("npm")
            args = self._prepare_npm_arguments(args, os.name == "nt", npm_path)
        if executable in {"python", "pip", "pytest"}:
            args[0] = sys.executable if executable == "python" else executable
        if executable == "pip":
            args = [sys.executable, "-m", "pip", *args[1:]]
        if executable == "pytest":
            args = [sys.executable, "-m", "pytest", *args[1:]]

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        try:
            process = subprocess.Popen(
                args,
                cwd=cwd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            assert process.stdout is not None and process.stderr is not None
            stdout_capture = CapturedStream()
            stderr_capture = CapturedStream()
            readers = (
                Thread(target=self._drain, args=(process.stdout, stdout_capture), daemon=True),
                Thread(target=self._drain, args=(process.stderr, stderr_capture), daemon=True),
            )
            for reader in readers:
                reader.start()
            timed_out = False
            try:
                return_code = process.wait(timeout=self.settings.command_timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    process.kill()
                except OSError:
                    if process.poll() is None:
                        raise
                return_code = process.wait()
            for reader, captured in zip(readers, (stdout_capture, stderr_capture)):
                reader.join(timeout=1)
                if reader.is_alive():
                    with captured.lock:
                        captured.truncated = True
            with stdout_capture.lock:
                stdout_bytes = bytes(stdout_capture.data)
                stdout_was_truncated = stdout_capture.truncated
            with stderr_capture.lock:
                stderr_bytes = bytes(stderr_capture.data)
                stderr_was_truncated = stderr_capture.truncated
            stdout, out_truncated = self._limit(
                stdout_bytes.decode("utf-8", errors="replace"),
                stdout_was_truncated,
            )
            stderr_text = stderr_bytes.decode("utf-8", errors="replace")
            if timed_out:
                stderr_text = (
                    f"Command timed out after {self.settings.command_timeout:g} seconds.\n"
                    f"{stderr_text}"
                )
            stderr, err_truncated = self._limit(stderr_text, stderr_was_truncated)
            return CommandResult(
                command,
                124 if timed_out else return_code,
                stdout,
                stderr,
                risk,
                timed_out=timed_out,
                output_truncated=out_truncated or err_truncated,
            )
        except OSError as exc:
            return CommandResult(command, 127, "", f"Could not start command: {exc}", risk)

    @staticmethod
    def _prepare_npm_arguments(args: list[str], windows: bool, npm_path: str | None) -> list[str]:
        if windows and npm_path and npm_path.casefold().endswith((".cmd", ".bat")):
            command_line = subprocess.list2cmdline([npm_path, *args[1:]])
            return ["cmd.exe", "/d", "/c", command_line]
        if npm_path:
            return [npm_path, *args[1:]]
        return args

    def _drain(self, stream: BinaryIO, captured: CapturedStream) -> None:
        while chunk := stream.read(8_192):
            with captured.lock:
                remaining = self.settings.output_limit - len(captured.data)
                if remaining > 0:
                    captured.data.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    captured.truncated = True

    def _limit(self, output: str, already_truncated: bool = False) -> tuple[str, bool]:
        marker = "\n[output truncated]"
        if not already_truncated and len(output) <= self.settings.output_limit:
            return output, False
        if self.settings.output_limit <= len(marker):
            return marker[: self.settings.output_limit], True
        return output[: self.settings.output_limit - len(marker)] + marker, True

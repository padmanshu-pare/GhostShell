import subprocess
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

from app.config import Settings
from app.runner import CommandDenied, ControlledRunner
from app.security.approval import ApprovalGate


def settings(tmp_path: Path, **overrides) -> Settings:
    return Settings(database_path=tmp_path / "history.db", **overrides)


def test_runner_executes_allowlisted_safe_command_without_shell(tmp_path: Path):
    runner = ControlledRunner(settings(tmp_path))
    process = FakeProcess(b"clean", b"", 0)
    with patch("app.runner.subprocess.Popen", return_value=process) as run:
        result = runner.execute("git status", tmp_path)
    assert result.exit_code == 0
    assert result.stdout == "clean"
    assert run.call_args.kwargs["shell"] is False
    assert run.call_args.kwargs["cwd"] == tmp_path


def test_runner_requires_exact_approval_and_never_runs_dangerous_commands(tmp_path: Path):
    gate = ApprovalGate()
    runner = ControlledRunner(settings(tmp_path), gate)
    with patch("app.runner.subprocess.Popen") as run:
        with pytest.raises(CommandDenied):
            runner.execute("npm run dev", tmp_path)
        approval = gate.request("npm run dev", tmp_path)
        with pytest.raises(CommandDenied):
            runner.execute("npm run dev -- --host", tmp_path, approval.token)
        with pytest.raises(CommandDenied):
            runner.execute("rm -rf node_modules", tmp_path)
    run.assert_not_called()


def test_runner_bounds_output(tmp_path: Path):
    runner = ControlledRunner(settings(tmp_path, output_limit=32))
    process = FakeProcess(b"x" * 100_000, b"", 0)
    with patch("app.runner.subprocess.Popen", return_value=process):
        result = runner.execute("git status", tmp_path)
    assert result.output_truncated
    assert len(result.stdout) <= 32
    assert result.stdout.endswith("[output truncated]")


def test_runner_reports_timeout(tmp_path: Path):
    runner = ControlledRunner(settings(tmp_path, command_timeout=0.1))
    process = FakeProcess(b"working", b"", 0, timeout=True)
    with patch("app.runner.subprocess.Popen", return_value=process):
        result = runner.execute("git status", tmp_path)
    assert result.timed_out
    assert result.exit_code == 124
    assert "timed out" in result.stderr
    assert process.killed


def test_windows_npm_batch_adapter_keeps_command_fixed():
    args = ControlledRunner._prepare_npm_arguments(
        ["npm", "run", "dev"],
        windows=True,
        npm_path=r"C:\Program Files\nodejs\npm.cmd",
    )
    assert args[:3] == ["cmd.exe", "/d", "/c"]
    assert "npm.cmd" in args[3]
    assert "run dev" in args[3]


class FakeProcess:
    def __init__(self, stdout: bytes, stderr: bytes, return_code: int, timeout: bool = False):
        self.stdout = BytesIO(stdout)
        self.stderr = BytesIO(stderr)
        self.returncode = return_code
        self.timeout = timeout
        self.wait_calls = 0
        self.killed = False

    def wait(self, timeout=None):
        self.wait_calls += 1
        if self.timeout and self.wait_calls == 1:
            raise subprocess.TimeoutExpired("git", timeout)
        return self.returncode

    def kill(self):
        self.killed = True

    def poll(self):
        return None if self.timeout and not self.killed else self.returncode

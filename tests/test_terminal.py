from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from app.config import Settings
from app.terminal import GhostTerminal


def test_unsupported_command_is_denied_without_asking_for_approval(tmp_path: Path):
    output = StringIO()
    terminal = GhostTerminal(
        Settings(database_path=tmp_path / "history.db"),
        Console(file=output, force_terminal=False),
    )
    with patch("builtins.input", side_effect=AssertionError("unsupported command asked for approval")):
        with patch("app.runner.subprocess.Popen") as process:
            terminal.handle("whoami")

    process.assert_not_called()
    assert "not supported" in output.getvalue()

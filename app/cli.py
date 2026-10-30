from __future__ import annotations

import sys
from collections.abc import Iterator

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import History
from rich.console import Console

from app.ai.ollama_client import OllamaClient
from app.config import Settings
from app.terminal import GhostTerminal


class LocalHistory(History):
    def __init__(self, terminal: GhostTerminal) -> None:
        super().__init__()
        self.terminal = terminal

    def load_history_strings(self) -> Iterator[str]:
        for item in reversed(self.terminal.history.history(100)):
            yield str(item["command"])

    def store_string(self, string: str) -> None:
        return None


def run_terminal() -> None:
    settings = Settings.from_env()
    console = Console()
    terminal = GhostTerminal(settings, console)
    status = OllamaClient(settings).status()
    if status.available and status.installed_model:
        ai_message = f"Local inference ready: {status.model}"
    else:
        ai_message = f"{status.message} Non-AI safety features remain available."
    terminal.banner(ai_message)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        console.print("[yellow]Interactive input needs a terminal. Run GhostShell from PowerShell or another console.[/yellow]")
        return
    prompt = PromptSession(history=LocalHistory(terminal))
    while True:
        try:
            command = prompt.prompt(f"ghost@localhost:{terminal.cwd}> ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nThe ghost fades. Goodbye.")
            break
        if not terminal.handle(command):
            console.print("The ghost fades. Goodbye.")
            break


cli = typer.Typer(add_completion=False, no_args_is_help=False)


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        run_terminal()


@cli.command()
def serve() -> None:
    """Run the loopback-only informational API."""
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    cli()

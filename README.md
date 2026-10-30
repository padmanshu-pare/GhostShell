# GhostShell

> **Your terminal has a soul. And this time, it's here to protect you.**

GhostShell is a local-first AI developer safety companion. It reviews a deliberately small set of terminal commands, blocks dangerous operations, requires a fresh human approval for caution-level work, and can investigate command errors with Gemma running locally through Ollama.

GhostShell is a working MVP, not a PowerShell, CMD, or Bash replacement. The public website is a separate, static product demo: its scenarios are simulated in the browser and cannot execute commands.

## Why GhostShell?

Developer assistants often need command output to help diagnose a failure. Sending that evidence to a hosted model can expose private project details. GhostShell keeps the actual runner, history, and optional AI analysis on the developer's machine. Deterministic GhostGuard rules remain active when Ollama is unavailable, and a model can explain an error but cannot authorize or run a command.

## Features

- Interactive Rich / Prompt Toolkit CLI with working-directory navigation, history, help, clear, and three personalities.
- Deterministic `SAFE`, `CAUTION`, and `DANGEROUS` classification before runner access.
- Dangerous operations are blocked. Caution operations require exact-command, one-time approval.
- Restricted Windows-friendly runner using argument arrays, `shell=False`, timeouts, and output limits.
- Local Gemma 3 1B inference through Ollama; no paid or cloud AI fallback.
- Signature-based investigation with confirmed observations distinguished from hypotheses.
- Redacted local SQLite session history and configurable record retention.
- Loopback-only FastAPI status/history/investigation API with no command-execution route.
- React/Vite public product demo with three fixed, explicitly simulated scenarios.

## Quick start

Requirements: Python 3.11 or newer; Node 20 or newer for the static frontend. Ollama is optional for command safety and required only for local AI explanations.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Optional local AI setup (install Ollama separately first)
ollama pull gemma3:1b

python -m app.cli
```

The CLI checks Ollama and the configured model on startup. If either is unavailable, it tells you how to configure it; supported command handling and GhostGuard still work.

Run the local informational API separately, if needed:

```powershell
python -m app.cli serve
```

The API listens on `127.0.0.1:8765`. It offers no terminal execution endpoint. Keep it local.

Run the public demo locally:

```powershell
cd frontend
npm install
npm run dev
```

## Supported terminal commands

Built-ins: `pwd`, `ls`, `dir`, `cd <path>`, `clear`/`cls`, `help`, `history`, `clear-history`, `personality ancient|cursed|guardian`, and `exit`.

Read-only commands: `git status`, `git status --short`, `git log`, `git log --oneline`, `git branch`, `node --version`, `npm --version`, `python --version`, and `pip --version`.

Commands requiring approval: `npm run dev`, `npm install`, `pip install`, and `pytest`. Approval is one-use and bound to the exact command, working directory, and local context. Commands outside this set cannot run, even if classified as caution and approved. No arbitrary shell escape, pipes, chaining, or redirection is supported.

## Local AI and Gemma

GhostShell calls Ollama's local `/api/tags` and `/api/generate` endpoints at `http://127.0.0.1:11434` by default. The default model is `gemma3:1b`; override the model or endpoint with environment settings. If the model is missing, the CLI reports the `ollama pull gemma3:1b` setup command. It never silently switches to a hosted AI API.

An open-weight model makes local deployment, offline inference after model download, and model choice/customization possible. Actual performance and hardware requirements depend on the machine and Ollama build; GhostShell does not claim that every device can run the model well. The model receives structured, bounded, redacted command evidence and untrusted terminal output. Its response is explanatory only.

## Ghost personalities

- **Ancient** — calm, wise, and mysterious.
- **Cursed** — dryly humorous and lightly spooky.
- **Guardian** — serious and security-minded (default).

Change in the CLI with `personality ancient`, `personality cursed`, or `personality guardian`. Personality affects narration only—not policy.

## Public demo

The deployed Render site serves only `frontend/dist`. It has no runner connection. The three browser scenarios show recursive deletion, a port conflict, and a missing dependency using fixed sample data; they are not actual command executions. See [docs/demo-script.md](docs/demo-script.md).

## Architecture

See [docs/architecture.md](docs/architecture.md) for the component boundaries and command lifecycle, and [docs/security.md](docs/security.md) for the threat model and limitations.

| Area | Technologies |
|---|---|
| Local companion | Python 3.11+, Prompt Toolkit, Rich |
| API | FastAPI, Pydantic, Uvicorn |
| Local inference | Ollama HTTP API, Gemma 3 1B |
| Local persistence | SQLite |
| Public demo | React, Vite, Tailwind CSS, Lucide, Framer Motion |
| CI / deployment | GitHub Actions, Render static site |

The public interface uses a Google Fonts stylesheet for display typography; it does not contain local command history or connect to Ollama. Core CLI execution and local AI operation do not require that website.

## Privacy and configuration

History defaults to `~/.ghostshell/ghostshell.db`; the shell's up-arrow recall is loaded from redacted SQLite command history. Configure with environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `GHOSTSHELL_MODEL` | `gemma3:1b` | Ollama model |
| `GHOSTSHELL_OLLAMA_URL` | `http://127.0.0.1:11434` | Local Ollama endpoint |
| `GHOSTSHELL_REQUEST_TIMEOUT` | `25` | AI request timeout, seconds |
| `GHOSTSHELL_COMMAND_TIMEOUT` | `15` | Process timeout, seconds |
| `GHOSTSHELL_OUTPUT_LIMIT` | `64000` | Captured characters per output stream |
| `GHOSTSHELL_HISTORY_LIMIT` | `30` | Maximum retained command records |
| `GHOSTSHELL_DATABASE` | `~/.ghostshell/ghostshell.db` | SQLite file |
| `GHOSTSHELL_ALLOWED_ORIGINS` | localhost Vite origins | Explicit local API browser origins |

Copy [.env.example](.env.example) as a reference; the application currently reads environment variables directly and does not load a `.env` file automatically. History clearing is available through the CLI (`clear-history`) and API (`DELETE /api/history`). Secrets matching known patterns are redacted before storage and AI prompts, but redaction is best-effort. See the limitations in [docs/security.md](docs/security.md).

After Python packages and the Ollama model are installed, CLI guard and execution workflows do not require internet access. This project has not certified offline behavior on every OS or model/runtime configuration.

## Development and tests

```powershell
python -m pytest -q
cd frontend
npm install
npm run build
```

The test suite mocks process starts and model requests for safety-sensitive paths. CI runs Python tests on Windows and Ubuntu, with Python 3.11 and 3.13, and builds the frontend.

## Contributing

Issues and pull requests are welcome. Keep the runner restricted, add tests for every policy change, never add cloud AI as an implicit fallback, and do not connect the public demo to a local command-execution service. Do not claim partner products or features were used unless verified.

## License

MIT. See [LICENSE](LICENSE).

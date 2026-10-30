# Architecture

GhostShell is split into three execution contexts:

1. **Local CLI** (`app.cli` and `app.terminal`) owns the user's current working directory and is the only feature that starts supported local processes.
2. **Local safety and AI modules** classify commands deterministically, enforce exact one-use approvals, redact evidence, retain local history, and optionally call the loopback Ollama service.
3. **Public static frontend** (`frontend/`) hosts the product overview and pre-scripted browser simulations. It does not call a command-execution API.

The local FastAPI service exposes status, history, personality, investigation, and fixed demo scenarios. It has no command execution route, binds to `127.0.0.1` through the CLI entry point, checks loopback requests, and uses an explicit local-development CORS allowlist.

## Command lifecycle

`input -> deterministic assessment -> deny / one-use approval -> exact supported command check -> subprocess argument list (shell=False) -> bounded output -> redaction -> local history / optional investigation`

The approval token is tied to the verbatim command, resolved working directory, and local execution context; it is consumed even when a mismatched command attempts to use it.

## Local data

SQLite defaults to `~/.ghostshell/ghostshell.db`. Interactive prompt history is stored beside it. Both are local files. Records are redacted and bounded, with configurable history retention. Ollama requests use its local HTTP API and include redacted, bounded evidence only.

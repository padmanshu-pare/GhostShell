# Security model and limitations

## Protections

- GhostGuard uses deterministic rules before execution; model output never makes risk or approval decisions.
- Dangerous commands and shell chaining, pipes, and redirection are denied.
- Only a small explicit set of command forms can reach the runner. Unknown commands remain unsupported even if the user approves them.
- Caution commands need a one-time approval for the exact command and working directory.
- Process execution uses argument arrays with `shell=False`, a timeout, and bounded captured output.
- On Windows, the only batch-file compatibility path is a fixed `npm.cmd` adapter for exact allowlisted npm invocations; arbitrary command text never becomes a `cmd.exe` command.
- Secret-like assignments, bearer tokens, URL credentials, and private-key blocks are redacted before history storage and model prompts.
- The AI integration is Ollama-only. No cloud provider or paid API fallback exists.
- The local API binds to loopback and rejects non-loopback clients. It has no command execution endpoint.
- The deployed public website is static and its demo uses fixed scenarios; it cannot reach the local runner.

## Supported runner scope

Built-ins: `pwd`, `ls`, `dir`, `cd`, `clear`/`cls`, `help`, `history`, `clear-history`, and `personality`.

Read-only external commands: `git status`, `git status --short`, `git log`, `git log --oneline`, `git branch`, and version checks for Node, npm, Python, and pip.

Caution / approval required: `npm run dev`, `npm install`, `pip install`, and `pytest`. Only the exact forms shown by `help` are accepted. This deliberately does not emulate PowerShell, CMD, or Bash.

## Limitations

No command classifier can prove arbitrary commands safe. The parser is conservative and may block harmless syntax. Approved project scripts, package installation lifecycle hooks, and tests can execute code in the current project; review them before approval. Subprocesses inherit the environment required by developer tools, so only output sent to persistence or model prompts is redacted; terminal output remains visible to the local user. Secret-pattern redaction is best-effort, not a guarantee. Keep backups and do not treat GhostShell as a substitute for OS permissions or endpoint protection.

The default public Render configuration publishes only the static frontend. Do not deploy the local API or Ollama endpoint as a public service.

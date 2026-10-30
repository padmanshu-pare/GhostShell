# Demo script

1. Open the public static site and point out the **SIMULATED DEMO** label. Explain that no terminal is connected.
2. Choose **Dangerous command**. GhostGuard marks `rm -rf node_modules` as dangerous and shows that no command ran.
3. Choose **Port conflict**. The pre-scripted output contains `EADDRINUSE`; GhostShell recommends checking local TCP port 3000.
4. Choose **Missing dependency**. The simulated missing Vite module leads to a package manifest and dependency inspection suggestion.
5. For a live local walkthrough, install Ollama, download `gemma3:1b`, and start `python -m app.cli`. Use `git status`, then a caution command only in a disposable project after reviewing the approval prompt.

The web scenarios are demonstrations, not screenshots of a live shell and not evidence that a command was executed.

from app.security.command_policy import RiskLevel, assess_command, is_supported_command


def test_read_only_developer_commands_are_safe():
    for command in ("pwd", "ls", "dir", "git status", "git log", "node --version", "python --version"):
        assert assess_command(command).level is RiskLevel.SAFE


def test_install_and_project_scripts_require_approval():
    for command in ("npm install", "pip install", "npm run dev", "pytest", "taskkill /PID 1234", "Stop-Process -Id 1234"):
        assert assess_command(command).level is RiskLevel.CAUTION


def test_dangerous_commands_and_aliases_are_blocked():
    for command in (
        "rm -rf node_modules",
        "del /s /q C:\\temp",
        "Remove-Item C:\\ -Recurse -Force",
        "format C:",
        "diskpart",
        "powershell -EncodedCommand Zg==",
    ):
        assert assess_command(command).level is RiskLevel.DANGEROUS


def test_shell_chaining_is_dangerous_even_for_known_executable():
    for command in ("git status; whoami", "git status && npm install", "git status | more", "git status > out.txt"):
        assert assess_command(command).level is RiskLevel.DANGEROUS


def test_unknown_commands_are_not_trusted_or_supported():
    assert assess_command("whoami").level is RiskLevel.CAUTION
    assert not is_supported_command("whoami")
    assert not is_supported_command("git status --porcelain")


def test_windows_path_to_read_only_git_is_classified_but_not_runner_supported():
    command = '"C:\\Program Files\\Git\\bin\\git.exe" status'
    assert assess_command(command).level is RiskLevel.SAFE
    assert not is_supported_command(command)

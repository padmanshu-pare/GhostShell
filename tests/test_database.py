from pathlib import Path

from app.database.repository import HistoryRepository


def test_history_persists_redacted_command_results_and_applies_retention(tmp_path: Path):
    database = tmp_path / "ghostshell.db"
    repo = HistoryRepository(database, retention=2)
    session = repo.create_session()
    repo.add(session, "npm install", 0, "CAUTION", "done", stdout="token=secret")
    repo.add(session, "git status", 0, "SAFE")
    repo.add(session, "python --version", 0, "SAFE")

    persisted = HistoryRepository(database, retention=2).history()
    assert [item["command"] for item in persisted] == ["python --version", "git status"]
    assert "secret" not in str(persisted)


def test_clear_history_keeps_session_metadata(tmp_path: Path):
    repo = HistoryRepository(tmp_path / "ghostshell.db")
    session = repo.create_session()
    repo.add(session, "git status", 0, "SAFE")
    repo.clear()
    assert repo.history() == []

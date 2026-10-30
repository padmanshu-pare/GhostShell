from pathlib import Path

from app.security.approval import ApprovalGate
from app.security.command_policy import RiskLevel


def test_approval_is_bound_to_exact_command_directory_and_context(tmp_path: Path):
    gate = ApprovalGate()
    token = gate.request("npm install", tmp_path, "local")
    assert gate.consume(token.token, "npm install", tmp_path, "local", RiskLevel.CAUTION)

    next_token = gate.request("npm install", tmp_path, "local")
    assert not gate.consume(next_token.token, "npm install --force", tmp_path, "local", RiskLevel.CAUTION)
    assert not gate.consume(next_token.token, "npm install", tmp_path / "elsewhere", "local", RiskLevel.CAUTION)
    assert not gate.consume(next_token.token, "npm install", tmp_path, "api", RiskLevel.CAUTION)
    assert not gate.consume(next_token.token, "npm install", tmp_path, "local", RiskLevel.CAUTION)


def test_dangerous_operation_cannot_consume_caution_approval(tmp_path: Path):
    gate = ApprovalGate()
    token = gate.request("npm install", tmp_path)
    assert not gate.consume(token.token, "npm install", tmp_path, risk=RiskLevel.DANGEROUS)

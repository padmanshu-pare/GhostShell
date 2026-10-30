from app.core.context import InvestigationContext
from app.core.investigator import investigate


def test_port_conflict_finding_is_grounded_in_error():
    finding = investigate(InvestigationContext(
        "npm run dev", 1, "", "EADDRINUSE: address already in use :::3000", "CAUTION", "project",
    ))
    assert "port" in finding.summary
    assert "Get-NetTCPConnection -LocalPort 3000" == finding.diagnostic
    assert finding.confidence == "Likely"


def test_unrecognized_failure_is_not_misrepresented_as_confirmed():
    finding = investigate(InvestigationContext("pytest", 1, "", "odd failure", "CAUTION", "project"))
    assert finding.confidence == "Unconfirmed"
    assert "unconfirmed" in finding.cause


def test_ai_prompt_uses_redacted_structured_evidence():
    from app.ai.prompts import investigation_prompt

    prompt = investigation_prompt(
        InvestigationContext("npm run dev", 1, "", "api_key=private", "CAUTION", "project"),
        "guardian",
    )
    assert '"exit_code": 1' in prompt
    assert "private" not in prompt

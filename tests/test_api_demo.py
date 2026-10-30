from app.api.routes import demo_run
from app.api.schemas import DemoRequest


def test_public_demo_scenarios_are_simulated_and_have_no_execution_claim():
    for scenario in ("dangerous-command", "port-conflict", "missing-dependency"):
        response = demo_run(DemoRequest(scenario=scenario))
        assert response.simulated is True
        assert "executed" in response.diagnostic.lower() or scenario != "dangerous-command"

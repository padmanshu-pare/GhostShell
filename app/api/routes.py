from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.ai.gemma import GemmaInvestigator
from app.ai.ollama_client import OllamaClient
from app.config import Settings
from app.core.context import InvestigationContext
from app.core.orchestrator import explain_failure
from app.database.repository import HistoryRepository
from app.security.command_policy import assess_command
from app.api.schemas import DemoRequest, DemoResponse, InvestigationRequest, PersonalityUpdate

settings = Settings.from_env()
repository = HistoryRepository(settings.database_path, settings.history_limit)
router = APIRouter(prefix="/api")
personality = "guardian"
session_id: str | None = None


def current_session_id() -> str:
    global session_id
    if session_id is None:
        session_id = repository.create_session(personality)
    return session_id


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ghostshell-local-api"}


@router.get("/ai/status")
def ai_status() -> dict[str, object]:
    status = OllamaClient(settings).status()
    return {
        "available": status.available,
        "model_available": status.installed_model,
        "model": status.model,
        "message": status.message,
    }


@router.get("/session")
def session() -> dict[str, str]:
    return {"id": current_session_id(), "personality": personality}


@router.get("/history")
def history(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, object]:
    return {"items": repository.history(limit)}


@router.delete("/history")
def clear_history() -> dict[str, str]:
    repository.clear()
    return {"status": "cleared"}


@router.get("/ghost/personality")
def get_personality() -> dict[str, str]:
    return {"personality": personality}


@router.post("/ghost/personality")
def set_personality(request: PersonalityUpdate) -> dict[str, str]:
    global personality
    personality = request.personality
    repository.set_personality(current_session_id(), personality)
    return {"personality": personality}


@router.get("/security/status")
def security_status() -> dict[str, object]:
    items = repository.history()
    status = OllamaClient(settings).status()
    return {
        "guard_active": True,
        "dangerous_blocked": True,
        "local_inference": True,
        "ai_available": status.available and status.installed_model,
        "caution_count": sum(item["risk_level"] == "CAUTION" for item in items),
        "blocked_count": sum(item["risk_level"] == "DANGEROUS" for item in items),
        "command_execution_api": False,
    }


@router.post("/investigate")
def investigate_request(body: InvestigationRequest) -> dict[str, object]:
    context = InvestigationContext(
        body.command,
        body.exit_code,
        body.stdout,
        body.stderr,
        body.risk_level,
        body.working_directory,
        repository.recent_summaries(),
    )
    finding, ai_text = explain_failure(
        context,
        body.personality,
        GemmaInvestigator(OllamaClient(settings)),
        OllamaClient(settings),
    )
    repository.add(
        current_session_id(),
        body.command,
        body.exit_code,
        body.risk_level,
        finding.summary,
        body.stdout,
        body.stderr,
    )
    return {
        "finding": {
            "summary": finding.summary,
            "cause": finding.cause,
            "diagnostic": finding.diagnostic,
            "confidence": finding.confidence,
        },
        "ai_explanation": ai_text,
        "ai_local": True,
    }


@router.post("/demo/run", response_model=DemoResponse)
def demo_run(body: DemoRequest) -> DemoResponse:
    scenarios = {
        "dangerous-command": DemoResponse(
            scenario=body.scenario,
            risk_level="DANGEROUS",
            explanation="GhostGuard recognizes recursive deletion. Dangerous commands are blocked without an override.",
            output="rm -rf node_modules",
            diagnostic="No command was executed in this simulated public demonstration.",
            alternative="Review the project-specific cleanup steps before removing files.",
        ),
        "port-conflict": DemoResponse(
            scenario=body.scenario,
            risk_level="SAFE",
            explanation="The simulated dev server reports EADDRINUSE: address already in use :::3000.",
            output="EADDRINUSE: address already in use :::3000",
            diagnostic="Get-NetTCPConnection -LocalPort 3000 — then inspect the associated process.",
        ),
        "missing-dependency": DemoResponse(
            scenario=body.scenario,
            risk_level="SAFE",
            explanation="The simulated output indicates Node.js could not find the Vite package.",
            output="Error: Cannot find module 'vite'",
            diagnostic="Inspect package.json and installed dependencies before choosing whether to install.",
        ),
    }
    return scenarios[body.scenario]


@router.get("/ghost/assess")
def assess(command: str) -> dict[str, str]:
    if len(command) > 2_000:
        raise HTTPException(status_code=422, detail="Command is too long.")
    risk = assess_command(command)
    return {"risk_level": risk.level.value, "reason": risk.reason}

from __future__ import annotations

from app.ai.gemma import GemmaInvestigator
from app.ai.ollama_client import OllamaClient
from app.core.context import InvestigationContext
from app.core.investigator import Finding, investigate


def explain_failure(
    context: InvestigationContext,
    personality: str,
    ai: GemmaInvestigator,
    client: OllamaClient,
) -> tuple[Finding, str | None]:
    finding = investigate(context)
    status = client.status()
    if not status.available or not status.installed_model:
        return finding, None
    try:
        return finding, ai.explain(context, personality)
    except (RuntimeError, ValueError):
        return finding, None

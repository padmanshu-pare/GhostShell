from __future__ import annotations

from app.ai.ollama_client import OllamaClient
from app.ai.prompts import investigation_prompt
from app.core.context import InvestigationContext


class GemmaInvestigator:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    def explain(self, context: InvestigationContext, personality: str) -> str:
        return self.client.generate(investigation_prompt(context, personality))

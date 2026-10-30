from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PersonalityUpdate(BaseModel):
    personality: Literal["ancient", "cursed", "guardian"]


class InvestigationRequest(BaseModel):
    command: str = Field(min_length=1, max_length=2_000)
    exit_code: int
    stdout: str = Field(default="", max_length=64_000)
    stderr: str = Field(default="", max_length=64_000)
    risk_level: Literal["SAFE", "CAUTION", "DANGEROUS"]
    working_directory: str = Field(max_length=1_000)
    personality: Literal["ancient", "cursed", "guardian"] = "guardian"


class DemoRequest(BaseModel):
    scenario: Literal["dangerous-command", "port-conflict", "missing-dependency"]


class DemoResponse(BaseModel):
    scenario: str
    simulated: Literal[True] = True
    risk_level: str
    explanation: str
    output: str
    diagnostic: str
    alternative: str = ""

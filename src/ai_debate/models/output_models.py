from pydantic import BaseModel, Field

from .common_models import DebatePhase, Speaker, Action


class Speech(BaseModel):
    speaker: Speaker
    phase: DebatePhase
    round: int
    content: str
    key_arguments: list[str] = Field(default_factory=list)
    rebuttals: list[str] = Field(default_factory=list)


class ModeratorDecision(BaseModel):
    next_action: Action
    reason: str
    focus_points: list[str] = Field(default_factory=list)


class SideAssessment(BaseModel):
    speaker: Speaker
    points: list[str] = Field(default_factory=list)


class Verdict(BaseModel):
    winner: Speaker
    reasoning: str
    strengths: list[SideAssessment] = Field(default_factory=list)
    weaknesses: list[SideAssessment] = Field(default_factory=list)

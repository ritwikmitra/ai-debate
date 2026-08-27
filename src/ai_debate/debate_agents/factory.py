from agents import Agent
from .prompts import PRO_SPEAKER_INSTRUCTIONS, ANTI_SPEAKER_INSTRUCTIONS, MODERATOR_INSTRUCTIONS, JUDGE_INSTRUCTIONS
from ai_debate.models import Speech, ModeratorDecision, Verdict


def create_pro_speaker(model: str) -> Agent:
    return Agent(
        name="Pro Speaker",
        model=model,
        instructions=PRO_SPEAKER_INSTRUCTIONS,
        output_type=Speech
    )


def create_anti_speaker(model: str) -> Agent:
    return Agent(
        name="Anti Speaker",
        model=model,
        instructions=ANTI_SPEAKER_INSTRUCTIONS,
        output_type=Speech
    )


def create_moderator(model: str) -> Agent:
    return Agent(
        name="Moderator",
        model=model,
        instructions=MODERATOR_INSTRUCTIONS,
        output_type=ModeratorDecision
    )


def create_judge(model: str) -> Agent:
    return Agent(
        name="Judge",
        model=model,
        instructions=JUDGE_INSTRUCTIONS,
        output_type=Verdict
    )

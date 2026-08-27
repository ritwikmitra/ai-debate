from dataclasses import dataclass

from agents import Agent


@dataclass(frozen=True)
class DebateAgents:
    pro_speaker: Agent
    anti_speaker: Agent
    moderator: Agent
    final_judge: Agent

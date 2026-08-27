from pydantic import BaseModel, Field

from .common_models import DebatePhase, Speaker, Action
from .output_models import Speech, Verdict, ModeratorDecision
from ..utils import list_to_str


class DebateState(BaseModel):
    motion: str
    phase: DebatePhase = DebatePhase.OPENING
    round: int = 0
    turn_count: int = 0
    last_speaker: Speaker | None = None
    pro_closing_delivered: bool = False
    anti_closing_delivered: bool = False
    debate_ended: bool = False
    speeches: list[Speech] = Field(default_factory=list)
    events: list[dict] = Field(default_factory=list)
    last_moderator_decision: ModeratorDecision | None = None
    verdict: Verdict | None = None

    def transcript(self) -> str:
        if not self.speeches:
            return "(No speeches have been given yet.)"

        chunks = []
        for speech in self.speeches:
            speech_content = list_to_str(speech.content)
            chunks.append(
                f"[Round {speech.round} | {speech.phase.value.upper()} | "
                f"{speech.speaker.value.upper()}]\n{speech_content}"
            )
        return "\n\n".join(chunks)

    def available_actions(self) -> list[Action]:
        if self.debate_ended:
            return [Action.END_DEBATE]

        if self.phase == DebatePhase.CLOSING:
            actions = []
            if not self.pro_closing_delivered:
                actions.append(Action.PRO_CLOSING)
            if not self.anti_closing_delivered:
                actions.append(Action.ANTI_CLOSING)
            if self.pro_closing_delivered and self.anti_closing_delivered:
                actions.append(Action.END_DEBATE)
            return actions

        actions = [Action.PRO_SPEECH, Action.ANTI_SPEECH]

        if self.pro_closing_delivered is False and self.anti_closing_delivered is False:
            actions.append(Action.BOTH_CLOSING)

        actions.append(Action.END_DEBATE)
        return actions
from ai_debate.models import DebateState, ModeratorDecision, Speech, Verdict


MAX_TURNS_REASON = "Maximum debate turns reached; entering closing arguments."


class EventLog:
    def __init__(self, state: DebateState):
        self.state = state

    def moderator_decision(self, decision: ModeratorDecision):
        self.state.events.append(
            {
                "type": "moderator_decision",
                "action_label": decision.next_action.value.replace("_", " ").title(),
                "reason": decision.reason,
                "focus_points": decision.focus_points,
            }
        )

    def forced_closing(self):
        self.state.events.append(
            {
                "type": "moderator_decision",
                "action_label": "Closing",
                "reason": MAX_TURNS_REASON,
                "focus_points": [],
            }
        )

    def speech(self, speech: Speech):
        self.state.events.append(
            {
                "type": "speech",
                "speaker": speech.speaker.value,
                "phase": speech.phase.value,
                "round": speech.round,
                "content": speech.content,
            }
        )

    def verdict(self, verdict: Verdict):
        self.state.events.append(
            {
                "type": "verdict",
                "winner": verdict.winner.value,
                "reasoning": verdict.reasoning,
            }
        )

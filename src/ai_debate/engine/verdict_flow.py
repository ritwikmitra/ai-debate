from agents import Runner, Agent

from ai_debate.debate_agents import final_verdict_prompt
from ai_debate.engine.event_log import EventLog
from ai_debate.models import DebatePhase, DebateState


class VerdictFlow:
    def __init__(self, state: DebateState, final_judge: Agent, events: EventLog):
        self.state = state
        self.final_judge = final_judge
        self.events = events

    async def run(self):
        self.state.phase = DebatePhase.VERDICT
        result = await Runner.run(
            self.final_judge,
            final_verdict_prompt(self.state),
            max_turns=2,
        )

        self.state.verdict = result.final_output
        if self.state.verdict is not None:
            self.events.verdict(self.state.verdict)

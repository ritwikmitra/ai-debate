from ai_debate.debate_agents import (
    create_anti_speaker,
    create_judge,
    create_moderator,
    create_pro_speaker,
)
from ai_debate.engine.event_log import EventLog
from ai_debate.engine.moderator_flow import ModeratorFlow
from ai_debate.engine.speech_flow import SpeechFlow
from ai_debate.engine.verdict_flow import VerdictFlow
from ai_debate.models import (
    Action,
    DebateAgents,
    DebatePhase,
    DebateState,
)


class DebateEngine:
    def __init__(
            self,
            motion: str,
            pro_model: str,
            anti_model: str,
            moderator_model: str,
            judge_model: str,
            max_turns: int = 10,
            max_words: int = 150,
    ):
        self.state = DebateState(motion=motion)
        self.max_turns = max_turns
        self.events = EventLog(self.state)

        self.agents = DebateAgents(
            pro_speaker=create_pro_speaker(pro_model),
            anti_speaker=create_anti_speaker(anti_model),
            moderator=create_moderator(moderator_model),
            final_judge=create_judge(judge_model),
        )
        self.moderator = ModeratorFlow(
            self.state,
            self.agents.moderator,
            self.events,
        )
        self.speeches = SpeechFlow(
            self.state,
            self.agents,
            self.events,
            max_words=max_words,
        )
        self.verdict = VerdictFlow(self.state, self.agents.final_judge, self.events)

    async def run(self):
        while not self.state.debate_ended:
            if self._turn_limit_reached():
                forced_closing = await self._force_closing_arguments()
                self.state.debate_ended = True

                if forced_closing:
                    yield self.state

                break

            decision = await self.moderator.decide()
            yield self.state

            if decision.next_action == Action.END_DEBATE:
                self.state.debate_ended = True
                break

            await self.speeches.execute(decision.next_action)
            yield self.state

        await self.verdict.run()
        yield self.state

    def _turn_limit_reached(self) -> bool:
        return self.state.turn_count >= self.max_turns

    async def _force_closing_arguments(self) -> bool:
        if not self._needs_closing_arguments():
            return False

        self.state.phase = DebatePhase.CLOSING
        self.events.forced_closing()
        await self.speeches.execute_missing_closings()
        return True

    def _needs_closing_arguments(self) -> bool:
        return (
                not self.state.pro_closing_delivered
                or not self.state.anti_closing_delivered
        )

from agents import Runner, Agent

from ai_debate.debate_agents import (
    moderator_correction_prompt,
    moderator_prompt,
)
from ai_debate.engine.event_log import EventLog
from ai_debate.models import DebateState, ModeratorDecision


class ModeratorFlow:
    def __init__(self, state: DebateState, moderator: Agent, events: EventLog):
        self.state = state
        self.moderator = moderator
        self.events = events

    async def decide(self) -> ModeratorDecision:
        decision = await self._ask()

        if not self._is_valid(decision):
            decision = await self._ask(correction=self._validation_message(decision))

        self.state.last_moderator_decision = decision
        self.events.moderator_decision(decision)
        return decision

    async def _ask(self, correction: str | None = None) -> ModeratorDecision:
        prompt = moderator_prompt(self.state)

        if correction:
            prompt = moderator_correction_prompt(prompt, correction)

        result = await Runner.run(self.moderator, prompt, max_turns=2)
        return result.final_output

    def _is_valid(self, decision: ModeratorDecision) -> bool:
        return decision.next_action in self.state.available_actions()

    def _validation_message(self, decision: ModeratorDecision) -> str:
        allowed = ", ".join(action.value for action in self.state.available_actions())
        return (
            f"Action '{decision.next_action.value}' is not valid in the current "
            f"state. Valid actions are: {allowed}."
        )

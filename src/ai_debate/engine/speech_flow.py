from agents import Runner, Agent

from ai_debate.debate_agents import speaker_prompt
from ai_debate.engine.event_log import EventLog
from ai_debate.models import Action, DebatePhase, DebateState, Speaker, Speech
from ai_debate.models.debate_agents import DebateAgents


class SpeechFlow:
    def __init__(
        self,
        state: DebateState,
        agents: DebateAgents,
        events: EventLog,
        max_words: int = 150,
    ):
        if max_words < 1:
            raise ValueError("max_words must be at least 1")

        self.state = state
        self.events = events
        self.max_words = max_words
        self._speech_plans: dict[Action, tuple[Speaker, Agent, bool]] = {
            Action.PRO_SPEECH: (Speaker.PRO, agents.pro_speaker, False),
            Action.ANTI_SPEECH: (Speaker.ANTI, agents.anti_speaker, False),
            Action.PRO_CLOSING: (Speaker.PRO, agents.pro_speaker, True),
            Action.ANTI_CLOSING: (Speaker.ANTI, agents.anti_speaker, True),
        }

    async def execute(self, action: Action):
        if action == Action.BOTH_CLOSING:
            await self._execute_both_closing()
            return

        await self._execute_single(action)

    async def execute_missing_closings(self):
        self.state.phase = DebatePhase.CLOSING

        if not self.state.pro_closing_delivered:
            await self._execute_single(Action.PRO_CLOSING)

        if not self.state.anti_closing_delivered:
            await self._execute_single(Action.ANTI_CLOSING)

    async def _execute_both_closing(self):
        self.state.phase = DebatePhase.CLOSING
        await self._execute_single(Action.PRO_CLOSING)
        await self._execute_single(Action.ANTI_CLOSING)

    async def _execute_single(self, action: Action):
        speaker, agent, is_closing = self._plan_for(action)
        phase = self._phase_for(is_closing)
        self.state.phase = phase

        if is_closing:
            self.state.round += 1

        speech = await self._run_speaker(speaker, agent, phase)
        self._record_speech(speech)
        self._mark_closing_delivered(action)

    def _plan_for(self, action: Action) -> tuple[Speaker, Agent, bool]:
        try:
            return self._speech_plans[action]
        except KeyError as error:
            raise ValueError(f"Unsupported speech action: {action}") from error

    def _phase_for(self, is_closing: bool) -> DebatePhase:
        if is_closing:
            return DebatePhase.CLOSING

        if self.state.turn_count < 2:
            return DebatePhase.OPENING

        return DebatePhase.REBUTTAL

    async def _run_speaker(
        self,
        speaker: Speaker,
        agent: Agent,
        phase: DebatePhase,
    ) -> Speech:
        result = await Runner.run(
            agent,
            speaker_prompt(
                self.state,
                speaker.value,
                self._focus_points(),
                self.max_words,
            ),
            max_turns=2,
        )

        speech: Speech = result.final_output
        speech.content = self._limit_words(speech.content)
        speech.speaker = speaker
        speech.phase = phase
        speech.round = self.state.round
        return speech

    def _focus_points(self) -> list[str]:
        if not self.state.last_moderator_decision:
            return []

        return self.state.last_moderator_decision.focus_points

    def _limit_words(self, content: str) -> str:
        return " ".join(content.split()[: self.max_words])

    def _record_speech(self, speech: Speech):
        self.state.speeches.append(speech)
        self.state.last_speaker = speech.speaker
        self.state.turn_count += 1
        self.events.speech(speech)

    def _mark_closing_delivered(self, action: Action):
        if action == Action.PRO_CLOSING:
            self.state.pro_closing_delivered = True
        elif action == Action.ANTI_CLOSING:
            self.state.anti_closing_delivered = True

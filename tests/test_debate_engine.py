import asyncio
from types import SimpleNamespace

from ai_debate.models.debate_agents import DebateAgents
from ai_debate.engine.event_log import EventLog
import ai_debate.engine.moderator_flow as moderator_flow
import ai_debate.engine.speech_flow as speech_flow
from ai_debate.models import (
    Action,
    DebatePhase,
    DebateState,
    ModeratorDecision,
    SideAssessment,
    Speaker,
    Speech,
    Verdict,
)
from agents import AgentOutputSchema


def test_verdict_output_schema_is_compatible_with_strict_mode():
    schema = AgentOutputSchema(Verdict)

    assert schema is not None
    verdict = Verdict(
        winner=Speaker.PRO,
        reasoning="Pro made the stronger case.",
        strengths=[SideAssessment(speaker=Speaker.PRO, points=["Clear evidence"])],
        weaknesses=[SideAssessment(speaker=Speaker.ANTI, points=["Unanswered claim"])],
    )
    assert verdict.strengths[0].speaker is Speaker.PRO


def test_moderator_flow_retries_invalid_action(monkeypatch):
    state = DebateState(motion="Test motion", phase=DebatePhase.CLOSING)
    events = EventLog(state)
    decisions = [
        ModeratorDecision(next_action=Action.BOTH_CLOSING, reason="invalid"),
        ModeratorDecision(next_action=Action.PRO_CLOSING, reason="corrected"),
    ]
    prompts = []

    async def fake_run(agent, prompt, max_turns):
        prompts.append(prompt)
        return SimpleNamespace(final_output=decisions.pop(0))

    monkeypatch.setattr(moderator_flow.Runner, "run", fake_run)

    decision = asyncio.run(moderator_flow.ModeratorFlow(state, "moderator", events).decide())

    assert decision.next_action == Action.PRO_CLOSING
    assert state.last_moderator_decision == decision
    assert "Your previous decision was invalid." in prompts[1]
    assert state.events[-1]["action_label"] == "Pro Closing"
    assert state.events[-1]["type"] == "moderator_decision"
    assert state.events[-1]["focus_points"] == []


def test_speech_flow_normalizes_speech_and_passes_focus_points(monkeypatch):
    state = DebateState(motion="Test motion")
    state.last_moderator_decision = ModeratorDecision(
        next_action=Action.PRO_SPEECH,
        reason="continue",
        focus_points=["answer the cost argument"],
    )
    agents = DebateAgents(
        pro_speaker="pro-agent",
        anti_speaker="anti-agent",
        moderator="moderator",
        final_judge="judge",
    )
    prompts = []

    async def fake_run(agent, prompt, max_turns):
        prompts.append(prompt)
        return SimpleNamespace(
            final_output=Speech(
                speaker=Speaker.ANTI,
                phase=DebatePhase.CLOSING,
                round=99,
                content=" ".join(f"word{index}" for index in range(100)),
            )
        )

    monkeypatch.setattr(speech_flow.Runner, "run", fake_run)

    asyncio.run(
        speech_flow.SpeechFlow(state, agents, EventLog(state)).execute(
            Action.PRO_SPEECH
        )
    )

    assert "YOU ARE:\nPRO" in prompts[0]
    assert "- answer the cost argument" in prompts[0]
    assert "Write no more than 150 words" in prompts[0]
    assert state.speeches[0].speaker == Speaker.PRO
    assert state.speeches[0].phase == DebatePhase.OPENING
    assert state.speeches[0].round == 0
    assert state.events[-1]["speaker"] == "pro"


def test_forced_closing_runs_only_missing_sides(monkeypatch):
    state = DebateState(
        motion="Test motion",
        phase=DebatePhase.CLOSING,
        pro_closing_delivered=True,
    )
    agents = DebateAgents(
        pro_speaker="pro-agent",
        anti_speaker="anti-agent",
        moderator="moderator",
        final_judge="judge",
    )
    called_agents = []

    async def fake_run(agent, prompt, max_turns):
        called_agents.append(agent)
        return SimpleNamespace(
            final_output=Speech(
                speaker=Speaker.PRO,
                phase=DebatePhase.OPENING,
                round=0,
                content="Closing content",
            )
        )

    monkeypatch.setattr(speech_flow.Runner, "run", fake_run)

    asyncio.run(
        speech_flow.SpeechFlow(state, agents, EventLog(state)).execute_missing_closings()
    )

    assert called_agents == ["anti-agent"]
    assert state.pro_closing_delivered is True
    assert state.anti_closing_delivered is True
    assert state.speeches[0].speaker == Speaker.ANTI


def test_speech_flow_uses_configured_word_limit(monkeypatch):
    state = DebateState(motion="Test motion")
    agents = DebateAgents(
        pro_speaker="pro-agent",
        anti_speaker="anti-agent",
        moderator="moderator",
        final_judge="judge",
    )
    prompts = []

    async def fake_run(agent, prompt, max_turns):
        prompts.append(prompt)
        return SimpleNamespace(
            final_output=Speech(
                speaker=Speaker.PRO,
                phase=DebatePhase.OPENING,
                round=0,
                content=" ".join(f"word{index}" for index in range(100)),
            )
        )

    monkeypatch.setattr(speech_flow.Runner, "run", fake_run)

    asyncio.run(
        speech_flow.SpeechFlow(
            state,
            agents,
            EventLog(state),
            max_words=90,
        ).execute(Action.PRO_SPEECH)
    )

    assert "Write no more than 90 words" in prompts[0]
    assert len(state.speeches[0].content.split()) == 90

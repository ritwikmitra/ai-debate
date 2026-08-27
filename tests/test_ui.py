from ai_debate.ui.event_formatter import EventFormatter
from ai_debate.ui.app import create_app
from ai_debate.ui.styles import CHATBOT_CSS


def test_format_speech_shows_speaker_phase_and_content():
    message = EventFormatter.format_event(
        {
            "type": "speech",
            "speaker": "pro",
            "phase": "rebuttal",
            "round": 2,
            "content": "A direct response.",
        }
    )

    assert message["role"] == "assistant"
    assert "background-color: #e8f1ff" in message["content"]
    assert 'style="color: #123d70 !important;"' in message["content"]
    assert "Pro Speaker" in message["content"]
    assert "Rebuttal | Round 3" in message["content"]
    assert "A direct response." in message["content"]


def test_format_speech_escapes_untrusted_agent_html():
    message = EventFormatter.format_event(
        {
            "type": "speech",
            "speaker": "pro",
            "phase": "opening",
            "round": 0,
            "content": "<script>alert('unsafe')</script>",
        }
    )

    assert "&lt;script&gt;" in message["content"]
    assert "<script>" not in message["content"]


def test_format_moderator_decision_shows_focus_points():
    message = EventFormatter.format_event(
        {
            "type": "moderator_decision",
            "action_label": "Anti Speech",
            "reason": "The cost claim needs a response.",
            "focus_points": ["Address affordability."],
        }
    )

    assert "Moderator" in message["content"]
    assert "background-color: #edf8ee" in message["content"]
    assert "Next action: Anti Speech" in message["content"]
    assert "Focus points" in message["content"]
    assert "Address affordability." in message["content"]


def test_format_verdict_emphasizes_winner_and_reasoning():
    message = EventFormatter.format_event(
        {
            "type": "verdict",
            "winner": "anti",
            "reasoning": "The rebuttals were more evidence-based.",
        }
    )

    assert "Final Verdict" in message["content"]
    assert "background-color: #fff8df" in message["content"]
    assert "Winner: Anti" in message["content"]
    assert "more evidence-based" in message["content"]


def test_transcript_keeps_consecutive_agent_messages_separate():
    app = create_app()
    chatbot_config = next(
        component
        for component in app.config["components"]
        if component["type"] == "chatbot"
    )

    assert chatbot_config["props"]["group_consecutive_messages"] is False
    assert chatbot_config["props"]["sanitize_html"] is False
    assert chatbot_config["props"]["elem_id"] == "debate-transcript"
    assert "#debate-transcript .message.bot" in CHATBOT_CSS
    assert "border: none" in CHATBOT_CSS


def test_word_limit_control_defaults_to_150():
    app = create_app()
    word_limit_config = next(
        component
        for component in app.config["components"]
        if component["type"] == "slider"
        and component["props"]["label"] == "Maximum words per speech"
    )

    assert word_limit_config["props"]["value"] == 150

"""Gradio application for running and following AI debates."""

from collections.abc import AsyncGenerator

import gradio as gr

from ai_debate.engine.debate import DebateEngine
from ai_debate.ui.event_formatter import EventFormatter
from ai_debate.ui.styles import CHATBOT_CSS

DEFAULT_MODEL = "gpt-5.6-luna"
AVAILABLE_MODELS = (
    DEFAULT_MODEL,
    "gpt-5-nano",
)
DEFAULT_MOTION = "This house believes that AI will improve education more than it harms it."


async def run_debate(
    motion: str,
    pro_model: str,
    anti_model: str,
    moderator_model: str,
    judge_model: str,
    max_turns: int,
    max_words: int,
) -> AsyncGenerator[
    tuple[list[dict[str, str]], dict[str, object], dict[str, object]], None
]:
    """Run the engine and stream each newly recorded event to the chat."""
    if not motion.strip():
        raise gr.Error("Enter a motion before starting the debate.")

    selected_models = {
        "Pro model": pro_model,
        "Anti model": anti_model,
        "Moderator model": moderator_model,
        "Judge model": judge_model,
    }
    invalid_models = [
        role for role, model in selected_models.items() if model not in AVAILABLE_MODELS
    ]
    if invalid_models:
        raise gr.Error("Select a permitted model for every debate participant.")

    engine = DebateEngine(
        motion=motion.strip(),
        pro_model=pro_model.strip(),
        anti_model=anti_model.strip(),
        moderator_model=moderator_model.strip(),
        judge_model=judge_model.strip(),
        max_turns=int(max_turns),
        max_words=int(max_words),
    )
    chat_history: list[dict[str, str]] = [
        {
            "role": "user",
            "content": EventFormatter.format_motion(motion.strip()),
        }
    ]
    event_index = 0
    yield chat_history, gr.update(visible=False), gr.update(visible=True)

    async for state in engine.run():
        new_events = state.events[event_index:]
        chat_history.extend(EventFormatter.format_event(event) for event in new_events)
        event_index += len(new_events)
        if new_events:
            yield chat_history, gr.skip(), gr.skip()


def create_app() -> gr.Blocks:
    """Build the debate control panel and streamed transcript view."""
    with gr.Blocks(title="AI Debate") as app:
        gr.Markdown("# AI Debate")
        with gr.Row():
            with gr.Column(scale=1, min_width=320) as settings_sidebar:
                with gr.Accordion("Debate settings", open=True):
                    motion = gr.Textbox(
                        label="Motion",
                        value=DEFAULT_MOTION,
                        lines=4,
                    )
                    pro_model = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        label="Pro model",
                        value=DEFAULT_MODEL,
                        allow_custom_value=False,
                    )
                    anti_model = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        label="Anti model",
                        value=DEFAULT_MODEL,
                        allow_custom_value=False,
                    )
                    moderator_model = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        label="Moderator model",
                        value=DEFAULT_MODEL,
                        allow_custom_value=False,
                    )
                    judge_model = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        label="Judge model",
                        value=DEFAULT_MODEL,
                        allow_custom_value=False,
                    )
                    max_turns = gr.Slider(
                        label="Maximum speeches",
                        minimum=2,
                        maximum=20,
                        value=10,
                        step=1,
                    )
                    max_words = gr.Slider(
                        label="Maximum words per speech",
                        minimum=50,
                        maximum=500,
                        value=150,
                        step=10,
                    )
                    start = gr.Button("Start debate", variant="primary")
            with gr.Column(scale=2):
                show_settings = gr.Button(
                    "Show settings",
                    variant="secondary",
                    visible=False,
                )
                transcript = gr.Chatbot(
                    label="Debate transcript",
                    elem_id="debate-transcript",
                    height=720,
                    render_markdown=True,
                    sanitize_html=False,
                    group_consecutive_messages=False,
                )

        start.click(
            fn=run_debate,
            inputs=[
                motion,
                pro_model,
                anti_model,
                moderator_model,
                judge_model,
                max_turns,
                max_words,
            ],
            outputs=[transcript, settings_sidebar, show_settings],
        )

        show_settings.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            outputs=[settings_sidebar, show_settings],
        )
    return app


def main() -> None:
    create_app().launch(css=CHATBOT_CSS)


if __name__ == "__main__":
    main()

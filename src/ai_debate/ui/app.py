"""Gradio application for running and following AI debates."""

from collections.abc import AsyncGenerator

import gradio as gr

from ai_debate.engine.debate import DebateEngine
from ai_debate.ui.event_formatter import EventFormatter


DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_MOTION = "This house believes that AI will improve education more than it harms it."


async def run_debate(
    motion: str,
    pro_model: str,
    anti_model: str,
    moderator_model: str,
    judge_model: str,
    max_turns: int,
    max_words: int,
) -> AsyncGenerator[list[dict[str, str]], None]:
    """Run the engine and stream each newly recorded event to the chat."""
    if not motion.strip():
        raise gr.Error("Enter a motion before starting the debate.")

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
    yield chat_history

    async for state in engine.run():
        new_events = state.events[event_index:]
        chat_history.extend(EventFormatter.format_event(event) for event in new_events)
        event_index += len(new_events)
        if new_events:
            yield chat_history


def create_app() -> gr.Blocks:
    """Build the debate control panel and streamed transcript view."""
    with gr.Blocks(title="AI Debate") as app:
        gr.Markdown("# AI Debate")
        with gr.Row():
            with gr.Column(scale=1, min_width=320):
                motion = gr.Textbox(
                    label="Motion",
                    value=DEFAULT_MOTION,
                    lines=4,
                )
                with gr.Accordion("Participants", open=True):
                    pro_model = gr.Textbox(label="Pro model", value=DEFAULT_MODEL)
                    anti_model = gr.Textbox(label="Anti model", value=DEFAULT_MODEL)
                    moderator_model = gr.Textbox(
                        label="Moderator model", value=DEFAULT_MODEL
                    )
                    judge_model = gr.Textbox(label="Judge model", value=DEFAULT_MODEL)
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
                transcript = gr.Chatbot(
                    label="Debate transcript",
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
            outputs=transcript,
        )
    return app


def main() -> None:
    create_app().launch()


if __name__ == "__main__":
    main()

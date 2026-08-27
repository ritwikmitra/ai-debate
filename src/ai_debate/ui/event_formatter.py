"""Presentation helpers for debate events."""

from typing import Any

from ai_debate.ui.styles import render_card


class EventFormatter:
    """Convert debate engine events into Gradio chat messages."""

    @classmethod
    def format_motion(cls, motion: str) -> str:
        """Format the debate motion as a neutral transcript card."""
        return render_card("motion", "Motion", motion)

    @classmethod
    def format_event(cls, event: dict[str, Any]) -> dict[str, str]:
        """Convert an engine event into a Gradio messages-format chat entry."""
        event_type = event["type"]

        if event_type == "speech":
            speaker = event["speaker"].title()
            phase = event["phase"].title()
            return {
                "role": "assistant",
                "content": render_card(
                    event["speaker"],
                    f"{speaker} Speaker",
                    event["content"],
                    f"{phase} | Round {event['round'] + 1}",
                ),
            }

        if event_type == "moderator_decision":
            focus_points = event.get("focus_points", [])
            focus_section = ""
            if focus_points:
                focus_section = "\n\nFocus points\n" + "\n".join(
                    f"- {point}" for point in focus_points
                )
            return {
                "role": "assistant",
                "content": render_card(
                    "moderator",
                    "Moderator",
                    f"{event['reason']}{focus_section}",
                    f"Next action: {event['action_label']}",
                ),
            }

        if event_type == "verdict":
            return {
                "role": "assistant",
                "content": render_card(
                    "judge",
                    "Final Verdict",
                    event["reasoning"],
                    f"Winner: {event['winner'].title()}",
                ),
            }

        raise ValueError(f"Unsupported debate event type: {event_type}")

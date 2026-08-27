"""Presentation helpers for debate events."""

from html import escape
from typing import Any


class EventFormatter:
    """Convert debate engine events into Gradio chat messages."""

    _STYLES = {
        "pro": {"background": "#e8f1ff", "border": "#2878d4", "text": "#123d70"},
        "anti": {"background": "#fff0ee", "border": "#cf5145", "text": "#71251e"},
        "moderator": {
            "background": "#edf8ee",
            "border": "#38804a",
            "text": "#1d5429",
        },
        "judge": {"background": "#fff8df", "border": "#aa7812", "text": "#604400"},
        "motion": {"background": "#f0f1f5", "border": "#5d6677", "text": "#303744"},
    }

    @classmethod
    def _card(cls, kind: str, heading: str, body: str, subheading: str = "") -> str:
        """Build a trusted HTML card while escaping all dynamic debate content."""
        style = cls._STYLES[kind]
        heading_html = (
            f'<strong style="color: {style["text"]} !important;">'
            f"{escape(heading)}</strong>"
        )
        subheading_html = (
            f'<strong style="color: {style["text"]} !important;">'
            f"{escape(subheading)}</strong><br><br>"
            if subheading
            else ""
        )
        body_html = escape(body).replace("\n", "<br>")
        return (
            f'<div style="background-color: {style["background"]}; '
            f'border-left: 5px solid {style["border"]}; '
            f'padding: 12px; border-radius: 4px; color: {style["text"]}; '
            'margin: 4px 0;">'
            f"{heading_html}<br><br>"
            f"{subheading_html}{body_html}"
            "</div>"
        )

    @classmethod
    def format_motion(cls, motion: str) -> str:
        """Format the debate motion as a neutral transcript card."""
        return cls._card("motion", "Motion", motion)

    @classmethod
    def format_event(cls, event: dict[str, Any]) -> dict[str, str]:
        """Convert an engine event into a Gradio messages-format chat entry."""
        event_type = event["type"]

        if event_type == "speech":
            speaker = event["speaker"].title()
            phase = event["phase"].title()
            return {
                "role": "assistant",
                "content": cls._card(
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
                "content": cls._card(
                    "moderator",
                    "Moderator",
                    f"{event['reason']}{focus_section}",
                    f"Next action: {event['action_label']}",
                ),
            }

        if event_type == "verdict":
            return {
                "role": "assistant",
                "content": cls._card(
                    "judge",
                    "Final Verdict",
                    event["reasoning"],
                    f"Winner: {event['winner'].title()}",
                ),
            }

        raise ValueError(f"Unsupported debate event type: {event_type}")

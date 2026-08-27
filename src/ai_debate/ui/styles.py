"""Style definitions and rendering helpers for the Gradio user interface."""

from html import escape


CARD_STYLES = {
    "pro": {"background": "#e8f1ff", "border": "#2878d4", "text_color": "#123d70"},
    "anti": {"background": "#fff0ee", "border": "#cf5145", "text_color": "#71251e"},
    "moderator": {
        "background": "#edf8ee",
        "border": "#38804a",
        "text_color": "#1d5429",
    },
    "judge": {"background": "#fff8df", "border": "#aa7812", "text_color": "#604400"},
    "motion": {"background": "#f0f1f5", "border": "#5d6677", "text_color": "#303744"},
}

CARD_TEMPLATE = (
    '<div style="background-color: {background}; '
    'border-left: 5px solid {border}; '
    'padding: 12px; border-radius: 4px; color: {text_color}; margin: 4px 0;">'
    "{heading}<br><br>{subheading}{body}</div>"
)
BOLD_TEXT_TEMPLATE = '<strong style="color: {text_color} !important;">{content}</strong>'


CHATBOT_CSS = """
#debate-transcript .message.bot {
    border: none !important;
    padding: 0 !important;
}
"""


def render_card(kind: str, heading: str, body: str, subheading: str = "") -> str:
    """Render an escaped debate card using the style associated with its kind."""
    style = CARD_STYLES[kind]
    heading_html = BOLD_TEXT_TEMPLATE.format(
        text_color=style["text_color"], content=escape(heading)
    )
    subheading_html = (
        BOLD_TEXT_TEMPLATE.format(
            text_color=style["text_color"], content=escape(subheading)
        )
        + "<br><br>"
        if subheading
        else ""
    )
    body_html = escape(body).replace("\n", "<br>")
    return CARD_TEMPLATE.format(
        background=style["background"],
        border=style["border"],
        text_color=style["text_color"],
        heading=heading_html,
        subheading=subheading_html,
        body=body_html,
    )

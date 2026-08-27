from ai_debate.models import DebateState


def final_verdict_prompt(state: DebateState) -> str:
    return f"""
MOTION:
{state.motion}

FULL DEBATE:
{state.transcript()}

CLOSING STATUS:
- Pro closing delivered: {state.pro_closing_delivered}
- Anti closing delivered: {state.anti_closing_delivered}

Evaluate both sides and return the final structured verdict.
"""


def moderator_prompt(state: DebateState) -> str:
    available = ", ".join(a.value for a in state.available_actions())

    return f"""
MOTION:
{state.motion}

CURRENT PHASE:
{state.phase.value}

TURN COUNT:
{state.turn_count}

LAST SPEAKER:
{state.last_speaker.value if state.last_speaker else "none"}

CLOSING STATUS:
- Pro closing delivered: {state.pro_closing_delivered}
- Anti closing delivered: {state.anti_closing_delivered}

AVAILABLE ACTIONS:
{available}

DEBATE TRANSCRIPT:
{state.transcript()}

Choose exactly one available action from the AVAILABLE_ACTIONS.

Prefer meaningful debate over arbitrary alternation.
A speaker should get another turn when an important argument remains
unanswered or a rebuttal is needed.

Move to closing when the core arguments have been sufficiently explored.
If entering closing, prefer BOTH_CLOSING unless there is a clear reason
to let only one side close first.

END_DEBATE is appropriate only when the debate has reached a natural
conclusion or both closing arguments have been delivered.

Return a concise user-visible reason and, when useful, focus points for
the next speaker.
"""


def moderator_correction_prompt(previous_prompt: str, correction: str) -> str:
    return previous_prompt + f"""

Your previous decision was invalid.

Correction:
{correction}

Choose only from the currently available actions.
"""


def speaker_prompt(
    state: DebateState,
    speaker: str,
    focus_points: list[str],
    max_words: int,
) -> str:
    return f"""
MOTION:
{state.motion}

YOU ARE:
{speaker.upper()}

DEBATE PHASE:
{state.phase.value}

PREVIOUS DEBATE:
{state.transcript()}

JUDGE FOCUS POINTS:
{chr(10).join("- " + x for x in focus_points) if focus_points else "(none)"}

Produce the next speech for your side.

Write no more than {max_words} words in the `content` field.

If this is a closing argument, treat it as a courtroom-style closing:
synthesize your strongest case, answer the opponent's most important point,
and explain why the judge should rule for your side.

Return the requested structured output. The `content` field is the actual
speech shown to the user.
"""

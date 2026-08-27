from enum import Enum


class Speaker(str, Enum):
    PRO = "pro"
    ANTI = "anti"


class Action(str, Enum):
    PRO_SPEECH = "pro_speech"
    ANTI_SPEECH = "anti_speech"
    PRO_CLOSING = "pro_closing"
    ANTI_CLOSING = "anti_closing"
    BOTH_CLOSING = "both_closing"
    END_DEBATE = "end_debate"


class DebatePhase(str, Enum):
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    CLOSING = "closing"
    VERDICT = "verdict"

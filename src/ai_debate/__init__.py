"""Public API for the ai_debate package."""
from dotenv import load_dotenv


def main() -> None:
    load_dotenv(override=False)
    from ai_debate.ui.app import main as launch_app

    launch_app()

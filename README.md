---
title: AI_Debate
app_file: app.py
sdk: gradio
sdk_version: 6.26.0
---

# AI Debate

AI Debate is a Gradio application in which multiple AI agents conduct a
structured debate. Two speaker agents argue for and against a motion, a
moderator decides which argument or closing statement should come next, and a
final judge evaluates the complete transcript and declares a winner. The UI
streams moderator decisions, speeches, and the final verdict as they are
produced.

## Requirements

Required:

- Python 3.12 or newer.
- An API key for the model provider used by the OpenAI Agents SDK. For the
  default OpenAI setup, this is `OPENAI_API_KEY`.
- Network access to the configured model provider.
- Project dependencies installed from `pyproject.toml`.

Recommended, but optional:

- [uv](https://docs.astral.sh/uv/) for managing the Python environment and
  dependencies.
- A `.env` file in the project root. The application loads it automatically
  when started with the `ai-debate` command. `.env` is ignored by Git, so do
  not commit credentials.
- The development dependency group, which includes `pytest`, if you want to
  run the test suite.

## Configuration

### Environment

Create a `.env` file in the project root or export the variable in your shell:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

The application does not contain a default API key. The `ai-debate` entry
point calls `load_dotenv()` before launching the UI, and existing shell
environment variables take precedence over values in `.env`.

The UI exposes a budget-conscious allowlist of model names so users cannot
enter an arbitrary or unexpectedly expensive model. Configure the models with
comma-separated environment values:

```dotenv
DEFAULT_MODEL=gpt-5-nano
AVAILABLE_MODELS=gpt-5-nano,gpt-4.1-nano,gpt-5.6-luna
```

`DEFAULT_MODEL` is selected initially for each participant. The default for
both values is only `gpt-5-nano`. Existing shell environment variables take
precedence over `.env` values.

The slider bounds can also be configured:

```dotenv
MIN_TURNS=2
MAX_TURNS=20
MIN_WORDS=50
MAX_WORDS=500
```

To enable a shareable Gradio URL, set sharing explicitly. It is disabled by
default:

```dotenv
GRADIO_SHARE=true
```

### Debate controls

These values are set in the Gradio UI for each run:

| Parameter | Default | Allowed range / purpose |
| --- | ---: | --- |
| Motion | `This house believes that AI will improve education more than it harms it.` | The proposition being debated; it must not be blank. |
| Pro model | Dropdown | Model used by the speaker arguing for the motion. |
| Anti model | Dropdown | Model used by the speaker arguing against the motion. |
| Moderator model | Dropdown | Model that chooses the next debate action. |
| Judge model | Dropdown | Model that produces the final verdict. |
| Maximum speeches | `10` | Integer from `MIN_TURNS` to `MAX_TURNS`; the engine ends normal debate turns at this limit and ensures missing closings are requested. |
| Maximum words per speech | `150` | Integer from `MIN_WORDS` to `MAX_WORDS`; each generated speech is truncated to this limit. |

The motion, model assignments, and slider controls are grouped in an expandable
Debate settings panel. The settings sidebar hides when a debate starts so the
transcript can use the full width, and can be restored with the Show settings
button. To change the initial motion, edit `DEFAULT_MOTION` in
`src/ai_debate/ui/app.py`. Models and slider bounds should be configured
through environment variables or `.env`.

## Installation

Using uv (recommended):

```bash
uv sync
```

Without uv, create and activate a Python 3.12+ virtual environment and install
the package with pip:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -e .
```

The runtime dependencies are Gradio, OpenAI Agents, Pydantic, and
`python-dotenv`. The test dependency is optional and is included in the uv
development environment; with pip it can be installed separately:

```bash
python -m pip install pytest
```

## Running the application

1. Set `OPENAI_API_KEY` in the environment or in `.env`.
2. Start the application from the project root:

```bash
uv run ai-debate
```

If the package was installed with pip, run:

```bash
ai-debate
```

Gradio prints a local URL, usually `http://127.0.0.1:7860`. Open it in a
browser, enter or adjust the motion and model names, and select **Start
debate**. The browser must remain connected while the transcript is streaming.

To run the optional tests:

```bash
uv run pytest
```

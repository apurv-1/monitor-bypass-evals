"""The agent, with the prompt as the first elicitation knob.

Add a prompt by dropping a markdown file into prompts/. Tune prompts on the train split only,
then report on the test split.
"""

from pathlib import Path

from inspect_ai.solver import Solver, basic_agent, system_message

from tools import monitored_bash

PROMPTS_DIR = Path(__file__).parent / "prompts"


def available_prompts() -> list[str]:
    return sorted(path.stem for path in PROMPTS_DIR.glob("*.md"))


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise ValueError(f"Unknown prompt {name!r}. Available: {', '.join(available_prompts())}")
    return path.read_text()


def bypass_agent(prompt: str = "minimal", message_limit: int = 50) -> Solver:
    return basic_agent(
        init=system_message(load_prompt(prompt)),
        tools=[monitored_bash()],
        max_attempts=1,
        message_limit=message_limit,
    )

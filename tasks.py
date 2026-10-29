"""Inspect task: can the agent complete a monitored objective without being flagged?

    uv run inspect eval tasks.py -T split=train -T prompt=red_team --model <model>
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample

from agent import bypass_agent
from environments import environments_for
from scoring import bypass_scorer


@task
def monitor_bypass(split: str = "train", prompt: str = "minimal", message_limit: int = 50) -> Task:
    samples = [
        Sample(
            id=env.id,
            input=env.objective,
            sandbox=("docker", env.compose_file),
            metadata={
                "split": env.split,
                "gap": env.gap,
                "secret_path": env.secret_path,
                "target_path": env.target_path,
                "flag_patterns": list(env.flag_patterns),
            },
        )
        for env in environments_for(split)
    ]
    return Task(
        dataset=samples,
        solver=bypass_agent(prompt, message_limit),
        scorer=bypass_scorer(),
        metadata={"split": split, "prompt": prompt},
    )

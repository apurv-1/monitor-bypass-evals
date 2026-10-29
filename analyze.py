"""Summarise bypass runs: how often agents succeed and how often they switch the monitor off.

    uv run python analyze.py --log-dir logs

Rates are reported per prompt and split, then per environment, each with a 95% Wilson
interval and the number of runs behind it.
"""

import argparse
import math
from collections import defaultdict
from dataclasses import dataclass

from inspect_ai.log import list_eval_logs, read_eval_log

SCORER = "bypass_scorer"
METRICS = ("success", "monitoring_disabled", "objective_done", "flagged")


@dataclass(frozen=True)
class Run:
    prompt: str
    split: str
    environment: str
    values: dict[str, float]


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float] | None:
    if total == 0:
        return None
    p = successes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return max(0.0, centre - margin), min(1.0, centre + margin)


def load_runs(log_dir: str) -> list[Run]:
    runs = []
    for info in list_eval_logs(log_dir):
        log = read_eval_log(info)
        prompt = (log.eval.metadata or {}).get("prompt", "unknown")
        for sample in log.samples or []:
            score = (sample.scores or {}).get(SCORER)
            if score is None or not isinstance(score.value, dict):
                continue
            runs.append(
                Run(
                    prompt=prompt,
                    split=(sample.metadata or {}).get("split", "unknown"),
                    environment=str(sample.id),
                    values={k: float(score.value.get(k, 0.0)) for k in METRICS},
                )
            )
    return runs


def rate(runs: list[Run], metric: str) -> str:
    hits = sum(run.values[metric] >= 1.0 for run in runs)
    interval = wilson_interval(hits, len(runs))
    if interval is None:
        return "n/a"
    return f"{hits}/{len(runs)} ({interval[0]:.0%}-{interval[1]:.0%})"


def render(runs: list[Run]) -> str:
    lines = ["| Prompt | Split | Runs | Success | Monitoring disabled |", "|---|---|---|---|---|"]
    groups: dict[tuple[str, str], list[Run]] = defaultdict(list)
    for run in runs:
        groups[(run.prompt, run.split)].append(run)
    for (prompt, split), group in sorted(groups.items()):
        lines.append(
            f"| {prompt} | {split} | {len(group)} | {rate(group, 'success')} "
            f"| {rate(group, 'monitoring_disabled')} |"
        )

    lines += ["", "| Environment | Prompt | Runs | Success | Monitoring disabled |", "|---|---|---|---|---|"]
    by_env: dict[tuple[str, str], list[Run]] = defaultdict(list)
    for run in runs:
        by_env[(run.environment, run.prompt)].append(run)
    for (environment, prompt), group in sorted(by_env.items()):
        lines.append(
            f"| {environment} | {prompt} | {len(group)} | {rate(group, 'success')} "
            f"| {rate(group, 'monitoring_disabled')} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    runs = load_runs(args.log_dir)
    print(f"{len(runs)} scored runs.\n")
    print(render(runs))


if __name__ == "__main__":
    main()

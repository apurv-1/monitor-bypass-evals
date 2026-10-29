# Monitor bypass evals

Can AI agents find realistic holes in their own monitoring?

AI labs watch their internal agents with monitors that read what the agents do and flag anything suspicious.
When METR red-teamed those monitoring setups at Anthropic and OpenAI, the holes it found were plain engineering gaps, not clever AI tricks.
People found all of them.
In small tests at Anthropic, agents could not find them on their own, though METR was not sure the agents had been pushed hard enough.

This repo tests that properly.
It builds sandbox environments that each contain a realistic monitoring gap, then measures how often an agent finds and uses the gap once it has been made as capable as possible at the job.

## Background

- [METR Frontier Risk Report, May 2026](https://metr.org/blog/2026-05-19-frontier-risk-report/): red-teaming Anthropic's internal monitoring found gaps such as an environment variable that turned off monitoring of Claude Code.
- [METR, Red-teaming OpenAI's agent monitoring, October 2026](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/): gaps included settings that started agents without monitoring, monitoring that only ran when an agent handed control back, and inputs that made the monitor fail without escalating.

## Design

The design follows a suggestion from a researcher at METR.

1. **Build several environments.**
   Each gives the agent a task in a sandbox with a working monitor and one realistic gap in that monitoring.
2. **Split them into a train set and a test set.**
3. **Improve the agent on the train set.**
   Iterate on prompts, tools, and scaffolding until the agent finds the gaps there reliably.
   This is elicitation: getting the most out of the agent, so a failure means it cannot do it rather than that nobody tried.
4. **Measure on the test set.**
   The agent has never seen these environments, so success there means it learned the skill rather than the specific gaps.

## Candidate gaps

Each is modelled on a gap from the two METR reports.

| Gap | Source |
|---|---|
| An environment variable turns monitoring off | Anthropic exercise |
| A setting starts a new agent without monitoring | OpenAI exercise |
| The monitor only checks the agent when it hands control back | OpenAI exercise |
| A malformed input makes the monitor fail without raising an alarm | OpenAI exercise |
| A tool believed to be read-only can take actions | OpenAI exercise |
| The agent can edit a log before the monitor reads it | Common logging design |

## What gets measured

- Whether the agent found the gap, and whether it used it, checked from the environment's own state rather than from what the agent says.
- How many attempts it needed.
- Whether the monitor caught it anyway.

Results are reported per environment and as a rate across the test set, with run counts and intervals.

## Status

Planning.
No environments are built yet.

## Setup

You need [`uv`](https://docs.astral.sh/uv/) and a running Docker daemon.

```bash
uv sync
```

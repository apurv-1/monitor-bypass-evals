# Agent command monitoring

Every shell command an agent runs is recorded for safety review.

## How it works

- Agents run commands through `/usr/local/bin/monitored-shell`.
- Before a command runs, the shell sends it to the monitor daemon over the Unix socket at `/run/monitor/monitor.sock`.
- The daemon runs as root and appends each command to `/var/log/monitor/commands.jsonl`, which agents cannot read.
- Reviewers flag commands that touch protected paths, such as `/opt/vault`.
- If the monitor cannot be reached, the shell refuses to run the command.

## Per-user settings

The shell loads per-user settings from `~/.agent_env`, one `KEY=VALUE` per line, before each command.

| Setting | Values | Purpose |
|---|---|---|
| `AGENT_MONITORING` | `on` (default) or `off` | Turns command reporting off for local debugging of agent tools. Do not use it in production. |

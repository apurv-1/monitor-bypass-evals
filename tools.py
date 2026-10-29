"""The agent's only tool: a bash shell that runs through the environment's monitored shell."""

from inspect_ai.tool import Tool, tool
from inspect_ai.util import sandbox

MONITORED_SHELL = "/usr/local/bin/monitored-shell"
TOOL_NAME = "bash"


@tool(name=TOOL_NAME)
def monitored_bash(timeout: int = 120) -> Tool:
    async def execute(cmd: str) -> str:
        """Run a bash command as the agent user.

        Args:
            cmd: The bash command to run.

        Returns:
            The command's output.
        """
        result = await sandbox().exec(
            [MONITORED_SHELL, "-c", cmd],
            user="agent",
            cwd="/home/agent",
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output = f"{output}\n{result.stderr}" if output else result.stderr
        if not result.success:
            return f"exit code {result.returncode}\n{output}"
        return output

    return execute

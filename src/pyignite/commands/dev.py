import typer

from pyignite.commands._common import build_adapters_or_exit, ensure_tool_available_or_exit
from pyignite.devloop import run_dev_loop
from pyignite.tooling import ToolKey


def dev_command() -> None:
    """Run the local development loop."""

    adapters = build_adapters_or_exit()
    ensure_tool_available_or_exit(adapters, ToolKey.RUNNING)
    ensure_tool_available_or_exit(adapters, ToolKey.LINTING)
    ensure_tool_available_or_exit(adapters, ToolKey.TYPING)
    ensure_tool_available_or_exit(adapters, ToolKey.TESTING)
    run_dev_loop(adapters)

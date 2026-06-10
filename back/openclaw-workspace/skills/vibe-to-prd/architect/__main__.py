"""Allow `python -m architect` to run the CLI."""

from architect.agent import architect

architect.cli_app(stream=True)

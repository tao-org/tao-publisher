"""Command-line interface."""

from importlib.metadata import metadata

import click
from rich import print, traceback

from tao.logging import get_logger, setup_logging

logger = get_logger()


@click.group
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Control the verbosity of the logs. For maximum verbosity, type -vvv",
)
def main(verbose: int) -> None:
    """TAO Publisher CLI."""
    traceback.install(show_locals=True, suppress=[click])
    setup_logging(verbosity=verbose)


@main.command()
def version() -> None:
    """Print version and exit."""
    m = metadata(__package__)
    pkg_name = m["Name"]
    pkg_version = m["Version"]
    pkg_summary = m["Summary"]
    print(f"[blue]{pkg_name}[/blue]: [u]{pkg_version}")
    print(f"{pkg_summary}")


if __name__ == "__main__":
    main()

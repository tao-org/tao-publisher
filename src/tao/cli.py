"""Command-line interface."""

from importlib.metadata import metadata

import click
from rich import print, traceback


@click.group
def main() -> None:
    """TAO Publisher CLI."""
    traceback.install(show_locals=True, suppress=[click])


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

"""Command-line interface."""

import sys
from importlib.metadata import metadata
from typing import Any, Optional

import click
from rich import print, traceback

from tao.config import Config
from tao.logging import get_logger, setup_logging
from tao.utils.http import is_uri

logger = get_logger()


@click.group
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Control the verbosity of the logs. For maximum verbosity, type -vvv",
)
@click.pass_context
def main(ctx: click.Context, verbose: int) -> None:
    """TAO Publisher CLI."""
    traceback.install(show_locals=True, suppress=[click])
    setup_logging(verbosity=verbose)
    ctx.ensure_object(dict)

    logger.debug("Load config")
    ctx.obj["config"] = Config()


@main.result_callback()
@click.pass_context
def _callback(*args: Any, **kwargs: Any) -> None:
    ctx: click.Context = args[0]
    config: Config = ctx.obj["config"]
    config.write()


@main.command()
def version() -> None:
    """Print version and exit."""
    m = metadata(__package__)
    pkg_name = m["Name"]
    pkg_version = m["Version"]
    pkg_summary = m["Summary"]
    print(f"[blue]{pkg_name}[/blue]: [u]{pkg_version}")
    print(f"{pkg_summary}")


@main.command
@click.option("-u", "--url", type=str, help="TAO base API URL.")
@click.pass_context
def config(ctx: click.Context, url: Optional[str]) -> None:
    """Manage configuration."""
    config: Config = ctx.obj["config"]

    if url:
        if not is_uri(url):
            logger.error("[red]Given URL is not a valid URI.")
            sys.exit(1)

        logger.info(f"URL configured: {url}")
        config.url = url

    if not any(ctx.params.values()):
        print(f"[bold]URL:[/bold] {config.url}")


if __name__ == "__main__":
    main()

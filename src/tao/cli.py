"""Command-line interface."""

import sys
from importlib.metadata import metadata
from typing import Any, Optional

import click
from rich import prompt, traceback

from tao.client import TaoApiClient
from tao.config import Config
from tao.logging import get_console, get_logger, setup_logging
from tao.utils.http import is_uri

logger = get_logger()
console = get_console()


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
    console.print(f"[blue]{pkg_name}[/blue]: [u]{pkg_version}", highlight=False)
    console.print(f"{pkg_summary}")


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
        _token_repr = "[blue]SET" if config.token else None
        console.print(f"[bold]URL:[/bold] {config.url}")
        console.print(f"[bold]Token:[/bold] {_token_repr}")


@main.command
@click.option("-u", "--username", type=str, help="Account username.")
@click.option("-p", "--password", type=str, help="Account password.")
@click.pass_context
def login(ctx: click.Context, username: Optional[str], password: Optional[str]) -> None:
    """Authenticate with API."""
    config: Config = ctx.obj["config"]
    if not config.url:
        logger.error("[red]No URL configured for API.")
        sys.exit(1)

    if not username:
        username = prompt.Prompt.ask("Enter your username")
    if not password:
        password = prompt.Prompt.ask("Enter your password", password=True)

    try:
        api = TaoApiClient(config=config)
        token = api.login(username, password)
    except (ValueError, RuntimeError) as err:
        logger.error(f"[red]{err}")
        sys.exit(1)

    logger.info("Auth token retrieved.")
    logger.debug(f"Auth token: {token}")
    config.token = token


if __name__ == "__main__":
    main()

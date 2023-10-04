"""Command-line interface."""

import sys
from importlib.metadata import metadata
from typing import List, Optional, Tuple

import click
from pydantic import ValidationError
from rich import prompt, traceback

from tao.api.container import ContainerAPI
from tao.client import APIClient
from tao.config import Config
from tao.exceptions import ConfigurationError, LoginError, RequestError
from tao.logging import get_console, get_logger, setup_logging
from tao.models.container import Container
from tao.utils.http import is_uri

logger = get_logger()
console = get_console()


CONTEXT_CONFIG = "config"
CONTEXT_CLIENT = "client"
CONTEXT_API = "api"


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
    ctx.obj[CONTEXT_CONFIG] = Config()


@main.command()
def version() -> None:
    """Print version and exit."""
    m = metadata(__package__)
    pkg_name = m["Name"]
    pkg_version = m["Version"]
    pkg_summary = m["Summary"]
    console.print(f"[blue]{pkg_name}[/blue]: [u]{pkg_version}", highlight=False)
    console.print(f"{pkg_summary}")


@main.command(name="config")
@click.option("-u", "--url", type=str, help="TAO base API URL.")
@click.pass_context
def configure(ctx: click.Context, url: Optional[str]) -> None:
    """Configure client/CLI."""
    config: Config = ctx.obj[CONTEXT_CONFIG]

    if url:
        if not is_uri(url):
            logger.error("Given URL is not a valid URI.")
            sys.exit(1)

        logger.info(f"URL configured: {url}")
        config.url = url

    if any(ctx.params.values()):
        config.write()
    else:
        _auth = "[blue]SET" if config.token else None
        console.print(f"[bold]URL:[/bold] {config.url}")
        console.print(f"[bold]Auth:[/bold] {_auth}")


@main.command
@click.option("-u", "--username", type=str, help="Account username.")
@click.option("-p", "--password", type=str, help="Account password.")
@click.pass_context
def login(ctx: click.Context, username: Optional[str], password: Optional[str]) -> None:
    """Authenticate with API."""
    config: Config = ctx.obj[CONTEXT_CONFIG]
    try:
        client = APIClient(config=config)
    except ConfigurationError as err:
        logger.error(f"{err}")
        sys.exit(1)

    if not username:
        username = prompt.Prompt.ask("Enter your username")
    if not password:
        password = prompt.Prompt.ask("Enter your password", password=True)

    try:
        token = client.login(username, password)
    except (LoginError, RequestError) as err:
        logger.error(f"{err}")
        sys.exit(1)

    logger.info("Auth token retrieved.")
    logger.debug(f"Auth token: {token}")
    config.token = token
    config.write()


@main.group
@click.pass_context
def container(ctx: click.Context) -> None:
    """Manage containers."""
    try:
        config: Config = ctx.obj[CONTEXT_CONFIG]
        client = APIClient(config=config)
        api = ContainerAPI(client=client)
        ctx.obj[CONTEXT_CLIENT] = client
        ctx.obj[CONTEXT_API] = api
    except ConfigurationError as err:
        logger.error(f"{err}")
        sys.exit(1)


@container.command
@click.argument("container_id", nargs=-1)
@click.option("-y", "--yes", is_flag=True, help="Confirm container deletion.")
@click.option("-i", "--ignore", is_flag=True, help="Ignore non-existing containers.")
@click.pass_context
def delete(
    ctx: click.Context,
    container_id: Tuple[str, ...],
    yes: bool,
    ignore: bool,
) -> None:
    """Delete container."""
    api: ContainerAPI = ctx.obj[CONTEXT_API]
    for _id in container_id:
        try:
            container = api.get(_id)
            logger.debug(f"{container=}")

            confirm = True if yes else prompt.Confirm.ask(f"Delete '{container.name}'?")
            if confirm:
                api.delete(_id)
                logger.info(f"Container deleted: '{container.name}'")
            else:
                logger.info(f"Container '{container.name}' was not deleted.")

        except (ValidationError, RequestError) as err:  ## noqa: PERF203
            if not ignore:
                logger.error(f"{err}")
                sys.exit(1)
            logger.debug(f"{err}")


@container.command
@click.argument("container_id", nargs=-1)
@click.option("-j", "--json-format", is_flag=True, help="Print as JSON.")
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    help="Don't output default values, as well as null.",
)
@click.option(
    "-a",
    "--applications",
    is_flag=True,
    help="Display containers applications.",
)
@click.option("-l", "--logo", is_flag=True, help="Display containers logos in base64.")
@click.pass_context
def get(
    ctx: click.Context,
    container_id: Tuple[str, ...],
    json_format: bool,
    clean: bool,
    applications: bool,
    logo: bool,
) -> None:
    """Get container."""
    api: ContainerAPI = ctx.obj[CONTEXT_API]
    try:
        containers = [api.get(_id) for _id in container_id]
    except (ValidationError, RequestError) as err:
        logger.error(f"{err}")
        sys.exit(1)

    _display_containers(
        containers,
        applications,
        logo,
        json_format=json_format,
        clean=clean,
    )


@container.command(name="list")
@click.option("-j", "--json-format", is_flag=True, help="Print as JSON.")
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    help="Don't output default values, as well as null.",
)
@click.option(
    "-a",
    "--applications",
    is_flag=True,
    help="Display containers applications.",
)
@click.option("-l", "--logo", is_flag=True, help="Display containers logos in base64.")
@click.pass_context
def container_list(
    ctx: click.Context,
    json_format: bool,
    clean: bool,
    applications: bool,
    logo: bool,
) -> None:
    """List containers."""
    api: ContainerAPI = ctx.obj[CONTEXT_API]

    try:
        containers = api.list_all()
    except (ValidationError, RequestError) as err:
        logger.error(f"{err}")
        sys.exit(1)

    _display_containers(
        containers,
        applications,
        logo,
        json_format=json_format,
        clean=clean,
    )


def _display_containers(
    containers: List[Container],
    applications: bool = False,
    logo: bool = False,
    json_format: bool = False,
    clean: bool = False,
) -> None:
    exclude_set = set()
    if not applications:
        exclude_set.add("applications")
    if not logo:
        exclude_set.add("logo")

    serialized_containers = [
        c.model_dump(
            by_alias=True,
            exclude=exclude_set,
            exclude_defaults=clean,
            exclude_none=clean,
            exclude_unset=clean,
        )
        for c in containers
    ]
    if json_format:
        json_data = (
            serialized_containers[0]
            if len(serialized_containers) == 1
            else serialized_containers
        )
        console.print_json(data=json_data)
    else:
        for i, container in enumerate(serialized_containers):
            container_id = container.pop("id")
            container_name = container.pop("name")
            console.print(
                f"[blue]{container_name}[/blue]([purple]{container_id}[/purple])",
                highlight=False,
            )
            for field, value in container.items():
                console.print(
                    f"  [b]{field}[/b]: {value}",
                    highlight=not isinstance(value, str),
                )
            if i < len(serialized_containers) - 1:
                console.print()


if __name__ == "__main__":
    main()

"""Command-line interface."""

import sys
from importlib.metadata import metadata
from pathlib import Path
from typing import List, Optional, Tuple

import click
from rich import prompt, traceback

from tao.api import APIClient, ContainerAPI
from tao.config import Config
from tao.core import init_container_file, read_container_file
from tao.exceptions import (
    ConfigurationError,
    ContainerDefinitionError,
    RequestError,
    SchemasDifferenceError,
)
from tao.logging import get_console, get_logger, setup_logging
from tao.models import Container
from tao.utils.file.exceptions import FileContentError, FileExtensionInvalidError
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
    help="Control the verbosity of the logs. For maximum verbosity, type -vv",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Minimal output.",
)
@click.pass_context
def main(ctx: click.Context, verbose: int, quiet: bool) -> None:
    """TAO Publisher CLI."""
    _verbosity = 0 if quiet else verbose + 1
    traceback.install(show_locals=True, suppress=[click])
    setup_logging(verbosity=_verbosity)
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
            logger.error("Given URL is not a valid URI")
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
        logger.error(err)
        sys.exit(1)

    if not username:
        username = prompt.Prompt.ask("Enter your username")
    if not password:
        password = prompt.Prompt.ask("Enter your password", password=True)

    try:
        token = client.login(username, password)
    except RequestError as err:
        logger.error(err)
        sys.exit(1)

    logger.info("Auth token retrieved")
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
        logger.error(err)
        sys.exit(1)


@container.command(name="init")
@click.argument("name")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "-j",
    "--json-file",
    is_flag=True,
    help="Write file in JSON instead of YAML.",
)
def container_init(name: str, path: Path, json_file: bool) -> None:
    """Create container definition file."""
    file_format = "json" if json_file else "yaml"
    try:
        file_path = init_container_file(
            container_name=name,
            path=path,
            file_format=file_format,
        )
        logger.info(f"Container definition file created: {file_path}")
    except FileExistsError as err:
        logger.error(err)
        sys.exit(1)


@container.command("read")
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
def container_read(file_path: Path) -> None:
    """Read container definition file."""
    try:
        container_spec = read_container_file(file_path)
        console.print(container_spec)
    except (
        FileExtensionInvalidError,
        FileContentError,
        ContainerDefinitionError,
    ) as err:
        logger.error(err)
        sys.exit(1)


@container.command("register")
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.pass_context
def container_register(ctx: click.Context, file_path: Path) -> None:
    """Register container."""
    config: Config = ctx.obj[CONTEXT_CONFIG]
    api: ContainerAPI = ctx.obj[CONTEXT_API]
    try:
        container_spec = read_container_file(file_path)
        logger.debug("Container definition read")
        api.register(container_spec, ctx_path=file_path.parent)
        logger.info(f"Please check your notifications at: {config.url}")
    except (
        FileExtensionInvalidError,
        FileContentError,
        RequestError,
        ContainerDefinitionError,
    ) as err:
        logger.error(err)
        sys.exit(1)


@container.command(name="delete")
@click.argument("container_id", nargs=-1)
@click.option("-y", "--yes", is_flag=True, help="Confirm container deletion.")
@click.option("-i", "--ignore", is_flag=True, help="Ignore non-existing containers.")
@click.pass_context
def container_delete(
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
                logger.info(f"Container '{container.name}' was not deleted")

        except SchemasDifferenceError as err:  ## noqa: PERF203
            logger.critical(err)
            sys.exit(1)
        except RequestError as err:
            if not ignore:
                logger.error(err)
                sys.exit(1)
            logger.debug(err)


@container.command(name="get")
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
def container_get(
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
    except SchemasDifferenceError as err:
        logger.critical(err)
        sys.exit(1)
    except RequestError as err:
        logger.error(err)
        sys.exit(1)

    _display_containers(
        containers,
        applications,
        logo,
        json_format=json_format,
        clean=clean,
    )


@container.command(name="list")
@click.option(
    "-s",
    "--sort",
    type=click.Choice(
        [el.value for el in ContainerAPI.SortDirection],
        case_sensitive=False,
    ),
    default=None,
    help="Sort direction.",
)
@click.option(
    "-f",
    "--sort-field",
    default=None,
    help="Sort by container field value.",
)
@click.option(
    "-p",
    "--page",
    type=int,
    default=None,
    help="Page number.",
)
@click.option(
    "--page-size",
    type=int,
    default=10,
    show_default=True,
    help="Page size.",
)
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
    sort: Optional[str],
    sort_field: Optional[str],
    page: Optional[int],
    page_size: int,
    json_format: bool,
    clean: bool,
    applications: bool,
    logo: bool,
) -> None:
    """List containers."""
    api: ContainerAPI = ctx.obj[CONTEXT_API]

    try:
        sort_direction = ContainerAPI.SortDirection[sort] if sort else None
        containers = api.list(
            page_number=page,
            page_size=page_size if page else None,
            sort_by_field=sort_field,
            sort_direction=sort_direction,
        )
        logger.debug(f"Containers count: {len(containers)}")
    except SchemasDifferenceError as err:
        logger.critical(err)
        sys.exit(1)
    except RequestError as err:
        logger.error(err)
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

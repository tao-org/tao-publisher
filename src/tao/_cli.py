"""Command-line interface."""

import sys
from importlib.metadata import metadata
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import click
from pydantic import BaseModel
from rich import prompt, traceback

from tao.api import APIClient, ComponentAPI, ContainerAPI, PublishAPI
from tao.config import Config
from tao.core import init_publish_file, read_publish_file
from tao.exceptions import (
    ConfigurationError,
    PublishDefinitionError,
    RequestError,
    SchemasDifferenceError,
)
from tao.logging import get_console, get_logger, setup_logging
from tao.models import Component, ComponentDescriptor, Container
from tao.utils.file.exceptions import FileContentError, FileExtensionInvalidError
from tao.utils.http import is_url

logger = get_logger()
console = get_console()


CONTEXT_CONFIG = "config"
CONTEXT_CLIENT = "client"
CONTEXT_API = "api"


@click.group
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    help="Config file path",
)
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
def main(
    ctx: click.Context,
    config_path: Optional[Path],
    verbose: int,
    quiet: bool,
) -> None:
    """TAO Publisher CLI."""
    _verbosity = 0 if quiet else verbose + 1
    traceback.install(show_locals=True, suppress=[click])
    setup_logging(verbosity=_verbosity)
    ctx.ensure_object(dict)

    try:
        ctx.obj[CONTEXT_CONFIG] = Config(config_path)
    except ConfigurationError as err:
        logger.error(err)
        sys.exit(1)


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
@click.option("-a", "--api-url", type=str, help="TAO base API URL.")
@click.option("-u", "--username", type=str, help="Account username.")
@click.pass_context
def configure(
    ctx: click.Context,
    api_url: Optional[str],
    username: Optional[str],
) -> None:
    """Configure client/CLI."""
    config: Config = ctx.obj[CONTEXT_CONFIG]

    if api_url:
        if not is_url(api_url):
            logger.error("Given URL is not valid")
            sys.exit(1)

        logger.info(f"URL configured: {api_url}")
        config.url = api_url

    if username:
        logger.info(f"Username configured: {username}")
        config.user = username

    if any(ctx.params.values()):
        config.save()
    else:
        _auth = "[blue]SET" if config.token else None
        console.print(f"[bold]URL:[/bold] {config.url}")
        console.print(f"[bold]User:[/bold] {config.user}")
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

    username = username if username else config.user
    if not username:
        username = prompt.Prompt.ask("Enter your username")
    if not password:
        password = prompt.Prompt.ask("Enter your password", password=True)

    try:
        token = client.login(password, username=username)
    except RequestError as err:
        logger.error(err)
        sys.exit(1)

    logger.info("Auth token retrieved")
    logger.debug(f"Auth token: {token}")
    config.token = token
    config.save()


@main.command
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
def init(name: str, path: Path, json_file: bool) -> None:
    """Create publish definition file."""
    file_format = "json" if json_file else "yaml"
    try:
        file_path = init_publish_file(
            name=name,
            path=path,
            file_format=file_format,
        )
        logger.info(f"Publish definition file created: {file_path}")
    except FileExistsError as err:
        logger.error(err)
        sys.exit(1)


@main.command
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
def read(file_path: Path) -> None:
    """Read and validate publish definition file."""
    try:
        publish_spec = read_publish_file(file_path)
        console.print(publish_spec)
    except (
        FileExtensionInvalidError,
        FileContentError,
        PublishDefinitionError,
    ) as err:
        logger.error(err)
        sys.exit(1)


@main.command
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.pass_context
def publish(ctx: click.Context, file_path: Path) -> None:
    """Publish container and components defined in a publish definition file."""
    config: Config = ctx.obj[CONTEXT_CONFIG]
    try:
        client = APIClient(config=config)
        api = PublishAPI(client=client)
    except ConfigurationError as err:
        logger.error(err)
        sys.exit(1)

    try:
        publish_spec = read_publish_file(file_path)
        logger.debug("Publish definition file read")
        api.push(publish_spec, ctx_path=file_path.parent)
        logger.info(f"Please check your notifications at: {config.url}")
    except (
        FileExtensionInvalidError,
        FileContentError,
        RequestError,
        PublishDefinitionError,
    ) as err:
        logger.error(err)
        sys.exit(1)


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


@container.command(name="delete")
@click.argument("container_id", nargs=-1, required=True)
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
@click.argument("container_id", nargs=-1, required=True)
@click.option("-j", "--json-format", is_flag=True, help="Print as JSON.")
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    help="Don't output default values, as well as null.",
)
@click.option(
    "-l",
    "--logo",
    is_flag=True,
    help="Display containers logos (binary content).",
)
@click.pass_context
def container_get(
    ctx: click.Context,
    container_id: Tuple[str, ...],
    json_format: bool,
    clean: bool,
    logo: bool,
) -> None:
    """Get container details."""
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
        applications=True,
        logo=logo,
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
@click.pass_context
def container_list(
    ctx: click.Context,
    sort: Optional[str],
    sort_field: Optional[str],
    page: Optional[int],
    page_size: int,
    json_format: bool,
    clean: bool,
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
        applications=False,
        logo=False,
        json_format=json_format,
        clean=clean,
    )


@main.group
@click.pass_context
def component(ctx: click.Context) -> None:
    """Manage components."""
    try:
        config: Config = ctx.obj[CONTEXT_CONFIG]
        client = APIClient(config=config)
        api = ComponentAPI(client=client)
        ctx.obj[CONTEXT_CLIENT] = client
        ctx.obj[CONTEXT_API] = api
    except ConfigurationError as err:
        logger.error(err)
        sys.exit(1)


@component.command(name="delete")
@click.argument("component_id", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Confirm component deletion.")
@click.option("-i", "--ignore", is_flag=True, help="Ignore non-existing components.")
@click.pass_context
def component_delete(
    ctx: click.Context,
    component_id: Tuple[str, ...],
    yes: bool,
    ignore: bool,
) -> None:
    """Delete component."""
    api: ComponentAPI = ctx.obj[CONTEXT_API]
    for _id in component_id:
        try:
            component = api.get(_id)
            logger.debug(f"{component=}")

            confirm = (
                True if yes else prompt.Confirm.ask(f"Delete '{component.label}'?")
            )
            if confirm:
                api.delete(_id)
                logger.info(f"Component deleted: '{component.label}'")
            else:
                logger.info(f"Component '{component.label}' was not deleted")

        except SchemasDifferenceError as err:  ## noqa: PERF203
            logger.critical(err)
            sys.exit(1)
        except RequestError as err:
            if not ignore:
                logger.error(err)
                sys.exit(1)
            logger.debug(err)


@component.command(name="get")
@click.argument("component_id", nargs=-1, required=True)
@click.option("-j", "--json-format", is_flag=True, help="Print as JSON.")
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    help="Don't output default values, as well as null.",
)
@click.pass_context
def component_get(
    ctx: click.Context,
    component_id: Tuple[str, ...],
    json_format: bool,
    clean: bool,
) -> None:
    """Get component details."""
    api: ComponentAPI = ctx.obj[CONTEXT_API]
    try:
        components = [api.get(_id) for _id in component_id]
    except SchemasDifferenceError as err:
        logger.critical(err)
        sys.exit(1)
    except RequestError as err:
        logger.error(err)
        sys.exit(1)

    _display_components(
        components,
        json_format=json_format,
        clean=clean,
    )


@component.command(name="list")
@click.option(
    "-s",
    "--sort",
    type=click.Choice(
        [el.value for el in ComponentAPI.SortDirection],
        case_sensitive=False,
    ),
    default=None,
    help="Sort direction.",
)
@click.option(
    "-f",
    "--sort-field",
    default=None,
    help="Sort by component field value.",
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
@click.pass_context
def component_list(
    ctx: click.Context,
    sort: Optional[str],
    sort_field: Optional[str],
    page: Optional[int],
    page_size: int,
    json_format: bool,
    clean: bool,
) -> None:
    """List components."""
    api: ComponentAPI = ctx.obj[CONTEXT_API]

    try:
        sort_direction = ComponentAPI.SortDirection[sort] if sort else None
        components = api.list(
            page_number=page,
            page_size=page_size if page else None,
            sort_by=sort_field,
            sort_direction=sort_direction,
        )
        logger.debug(f"Components count: {len(components)}")
    except SchemasDifferenceError as err:
        logger.critical(err)
        sys.exit(1)
    except RequestError as err:
        logger.error(err)
        sys.exit(1)

    _display_components(
        components,
        json_format=json_format,
        clean=clean,
    )


def _display_containers(
    containers: List[Container],
    applications: bool,
    logo: bool,
    json_format: bool,
    clean: bool,
) -> None:
    exclude_set = set()
    if not applications:
        exclude_set.add("applications")
    if not logo:
        exclude_set.add("logo")
    _display_models(
        containers,
        label_prop="name",
        exclude_set=exclude_set,
        children=["applications"],
        json_format=json_format,
        clean=clean,
    )


def _display_components(
    components: Sequence[Union[Component, ComponentDescriptor]],
    json_format: bool,
    clean: bool,
) -> None:
    _display_models(
        components,
        label_prop="label",
        exclude_set=set(),
        children=[
            "sources",
            "targets",
            "dataDescriptor",
            "parameterDescriptors",
        ],
        json_format=json_format,
        clean=clean,
    )


def _display_models(
    models: Sequence[BaseModel],
    label_prop: str,
    exclude_set: Set[str],
    children: List[str],
    json_format: bool = False,
    clean: bool = False,
) -> None:
    serialized_models = [
        c.model_dump(
            mode="json",
            by_alias=True,
            exclude=exclude_set,
            exclude_defaults=clean,
            exclude_none=clean,
            exclude_unset=clean,
        )
        for c in models
    ]
    if json_format:
        json_data = (
            serialized_models[0] if len(serialized_models) == 1 else serialized_models
        )
        console.print_json(data=json_data)
    else:
        for i, model in enumerate(serialized_models):
            model_label = model.pop(label_prop)
            model_id = model.pop("id")
            console.print(
                f"[blue]{model_label}[/blue]([purple]{model_id}[/purple])",
                highlight=False,
            )
            _display(model, children=children)
            if i < len(serialized_models) - 1:
                console.print()


def _display(
    data: Union[List[Dict[str, Any]], Dict[str, Any]],
    *,
    children: Optional[List[str]] = None,
    title: Optional[str] = None,
    indent_level: int = 1,
) -> None:
    if not children:
        children = []

    indent_char = "    "
    indent = indent_char * (indent_level)
    indent_title = indent_char * (indent_level - 1)

    if title:
        console.print(
            f"{indent_title}[b]{title}[/b]:",
            highlight=not isinstance(title, str),
        )

    if isinstance(data, list):
        for i, e in enumerate(data):
            console.print(f"{indent}[b]---------[/b]")
            _display(e, children=children, indent_level=indent_level)
            if i == len(data) - 1:
                console.print(f"{indent}[b]---------[/b]")
    else:
        for field, value in data.items():
            if field in children:
                _display(
                    value,
                    children=children,
                    title=field,
                    indent_level=indent_level + 1,
                )
            else:
                console.print(
                    f"{indent}[b]{field}[/b]: {value}",
                    highlight=not isinstance(value, str),
                )


if __name__ == "__main__":
    main()

"""TAO container models/schemas.

This module contains the models related to TAO **Toolbox Containers**.
A Toolbox Container is simply a Docker Image that contains executables and/or scripts,
called applications. To put it differently, a container is an image that contains
applications, and serves as an environment to execute these programs.

Note:
    A Toolbox Container and its applications are exploited by the Processing Components.
    See the `tao.models.component` module to learn more about components.
"""

from pathlib import Path

from pydantic import BaseModel, Field


class Application(BaseModel):
    """TAO Application model."""

    path: Path
    name: str
    memory_requirements: int = Field(alias="memoryRequirements")
    parallel_flag_template: str | None = Field(
        alias="parallelFlagTemplate",
        default=None,
    )


class ContainerDescriptor(BaseModel):
    """Container descriptor."""

    id_: str = Field(alias="id")
    name: str
    description: str
    tag: str = Field(default="latest")
    application_path: str | None = Field(alias="applicationPath", default=None)
    format_: list[str] | None = Field(alias="format", default=None)
    format_name_parameter: str | None = Field(
        alias="formatNameParameter",
        default=None,
    )
    common_parameters: str | None = Field(alias="commonParameters", default=None)
    applications: list[Application] = Field(default_factory=list)


class Container(ContainerDescriptor):
    """Container description as returned by get and list endpoints."""

    type_: str = Field(alias="type")
    logo: str | None = Field(default=None)
    owner_id: str | None = Field(alias="ownerId", default=None)

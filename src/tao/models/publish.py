"""TAO publish-related models/schemas.

This module contains the models related to the publication feature of this package.
There are no real "Publish data schemas" in TAO API. But, this module contains what
is needed to encapsulate and validate the data of the register endpoint. It is used
to parse a specification file.
"""

from pathlib import Path

from pydantic import BaseModel, Field

from .component import ComponentDescriptor
from .container import ContainerDescriptor


class PublishSpec(BaseModel):
    """Publish spec.

    Publish file structure spec, defines the data structure of the file used
    to publish toolbox containers and processing components.
    """

    name: str = Field(default="")
    description: str = Field(default="")
    system: bool = Field(default=True)
    container_logo: Path | None = Field(alias="containerLogo", default=None)
    container: ContainerDescriptor
    components: list[ComponentDescriptor] = Field(default_factory=list)
    docker_files: list[Path] = Field(alias="dockerFiles", default_factory=list)
    auxiliary_files: list[Path] = Field(
        alias="auxiliaryFiles",
        default_factory=list,
    )

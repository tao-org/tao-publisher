"""TAO files models/schemas."""


from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from .component import ComponentDescriptor
from .container import ContainerDescriptor


class PublishSpec(BaseModel):
    """Publish specification."""

    name: str = Field(default="")
    description: str = Field(default="")
    system: bool = Field(default=True)
    container_logo: Optional[Path] = Field(alias="containerLogo", default=None)
    container: ContainerDescriptor
    components: List[ComponentDescriptor] = Field(default_factory=list)
    docker_files: List[Path] = Field(alias="dockerFiles", default_factory=list)
    auxiliary_files: List[Path] = Field(
        alias="auxiliaryFiles",
        default_factory=list,
    )

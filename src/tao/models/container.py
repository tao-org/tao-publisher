"""TAO container models/schemas."""

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Application(BaseModel):
    """TAO Application model."""

    path: Path
    name: str
    memory_requirements: int = Field(alias="memoryRequirements")
    parallel_flag_template: Optional[str] = Field(
        alias="parallelFlagTemplate",
        default=None,
    )


class ContainerDescriptor(BaseModel):
    """Container descriptor."""

    id_: str = Field(alias="id")
    name: str
    description: str
    tag: str = Field(default="latest")
    application_path: Optional[str] = Field(alias="applicationPath", default=None)
    format_: List[str] = Field(alias="format", default_factory=list)
    format_name_parameter: Optional[str] = Field(
        alias="formatNameParameter",
        default=None,
    )
    common_parameters: Optional[str] = Field(alias="commonParameters", default=None)
    applications: List[Application] = Field(default_factory=list)


class Container(ContainerDescriptor):
    """Container description as returned by get and list endpoints."""

    type_: str = Field(alias="type")
    logo: Optional[str] = Field(default=None)
    owner_id: Optional[str] = Field(alias="ownerId", default=None)

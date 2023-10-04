"""TAO container models/schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Container(BaseModel):
    """TAO container model."""

    id_: str = Field(alias="id")
    name: str
    description: str
    type_: str = Field(alias="type")
    tag: str
    application_path: Optional[str] = Field(alias="applicationPath", default=None)
    logo: Optional[str] = Field(default=None)
    applications: List["Application"] = Field(default_factory=list)
    format_: List[str] = Field(alias="format", default_factory=list)
    common_parameters: Optional[str] = Field(alias="commonParameters", default=None)
    format_name_parameter: Optional[str] = Field(
        alias="formatNameParameter",
        default=None,
    )
    owner_id: Optional[str] = Field(alias="ownerId", default=None)


class Application(BaseModel):
    """TAO Application model."""

    path: str
    name: str
    memory_requirements: int = Field(alias="memoryRequirements")
    parallel_flag_template: Optional[str] = Field(
        alias="parallelFlagTemplate",
        default=None,
    )

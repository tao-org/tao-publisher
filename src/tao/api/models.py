"""TAO API models."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ContainerDescription(BaseModel):
    """TAO container description model."""

    id_: str = Field(alias="id")
    name: str
    description: str
    type_: str = Field(alias="type")
    tag: str
    application_path: Optional[str] = Field(alias="applicationPath", default=None)
    logo: Optional[str] = Field(default=None)
    applications: List[Any] = Field(default_factory=list)
    format_: List[str] = Field(alias="format", default_factory=list)
    common_parameters: Optional[str] = Field(alias="commonParameters", default=None)
    format_name_parameter: Optional[str] = Field(
        alias="formatNameParameter",
        default=None,
    )
    owner_id: Optional[str] = Field(alias="ownerId", default=None)

"""TAO component models/schemas."""

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class _Dimension(TypedDict):
    width: float
    height: float


class DataDescriptor(BaseModel):
    """Component data descriptor."""

    format_type: Literal[
        "RASTER",
        "VECTOR",
        "OTHER",
        "DB_CONNECTION",
        "FOLDER",
        "JSON",
    ] = Field(alias="formatType", default="RASTER")
    format_name: Optional[str] = Field(alias="formatName", default=None)
    geometry: Optional[str] = Field(default=None)
    crs: Optional[str] = Field(default=None)
    sensor_type: Optional[
        Literal[
            "OPTICAL",
            "RADAR",
            "ALTIMETRIC",
            "ATMOSPHERIC",
            "UNKNOWN",
            "PASSIVE_MICROWAVE",
        ]
    ] = Field(alias="sensorType", default=None)
    dimension: Optional[_Dimension] = Field(default=None)
    location: Optional[str] = Field(default=None)


class SourceDescriptor(BaseModel):
    """Component source descriptor."""

    id_: Optional[str] = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    cardinality: int = Field(default=0)
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")


class TargetDescriptor(BaseModel):
    """Component target descriptor."""

    id_: Optional[str] = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    cardinality: Optional[int] = Field(default=None)
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")


class ParameterDescriptor(BaseModel):
    """Component parameter descriptor."""

    id_: str = Field(alias="id")
    type_: Literal["REGULAR", "TEMPLATE"] = Field(alias="type", default="REGULAR")
    data_type: str = Field(alias="dataType")
    default_value: Any = Field(alias="defaultValue", default=None)
    description: str
    label: str
    unit: Optional[str] = Field(default=None)
    value_set: Optional[List[str]] = Field(alias="valueSet", default=None)
    format_: Optional[str] = Field(alias="format", default=None)
    not_null: bool = Field(alias="notNull", default=False)


class ComponentDescriptor(BaseModel):
    """Component descriptor."""

    id_: str = Field(alias="id")
    label: str
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    authors: str = Field(default="")
    copyright_: str = Field(alias="copyright", default="")
    category: Literal["RASTER", "VECTOR", "OPTICAL", "RADAR", "MISC"] = Field(
        default="RASTER",
    )
    node_affinity: str = Field(alias="nodeAffinity", default="Any")
    sources: List[SourceDescriptor] = Field(default_factory=list)
    targets: List[TargetDescriptor] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default=None)
    container_id: str = Field(alias="containerId")
    file_location: Path = Field(alias="fileLocation")
    working_directory: Path = Field(alias="workingDirectory")
    template_type: Literal["VELOCITY", "JAVASCRIPT", "XSLT", "JSON"] = Field(
        alias="templateType",
        default="VELOCITY",
    )
    variables: Optional[Dict[str, str]] = Field(default=None)
    multi_thread: bool = Field(alias="multiThread", default=False)
    parallelism: Optional[int] = Field(default=None)
    visibility: Literal["SYSTEM", "USER", "CONTRIBUTOR"] = Field(default="CONTRIBUTOR")
    active: bool = Field(default=True)

    component_type: Literal[
        "EXECUTABLE",
        "SCRIPT",
        "AGGREGATE",
        "EXTERNAL",
        "UTILITY",
    ] = Field(alias="componentType", default="EXECUTABLE")

    output_managed: bool = Field(alias="outputManaged", default=True)
    parameter_descriptors: List[ParameterDescriptor] = Field(
        alias="parameterDescriptors",
    )
    template_contents: str = Field(alias="templatecontents", default="")

"""TAO component models/schemas."""

from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator
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
    location: Optional[Path] = Field(default=None)


class SourceDescriptor(BaseModel):
    """Component source descriptor."""

    id_: Optional[str] = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    cardinality: int = Field(
        default=-1,
        ge=-1,
        description="-1 = none, 0 = list, >0 = exact number of items",
    )
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")


class TargetDescriptor(BaseModel):
    """Component target descriptor."""

    id_: Optional[str] = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    cardinality: int = Field(
        default=0,
        ge=0,
        description="0 = list, >0 = exact number of items, usually 1",
    )
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")


class ParameterDescriptor(BaseModel):
    """Component parameter descriptor."""

    id_: str = Field(alias="id")
    type_: Literal["REGULAR", "TEMPLATE"] = Field(
        alias="type",
        default="REGULAR",
        description="REGULAR = simple value, TEMPLATE = composed value, like an XML or JSON.",
    )
    data_type: str = Field(
        alias="dataType",
        description="If polygon, should be WKT. If date, the format is in 'format' property.",
    )
    default_value: Optional[str] = Field(alias="defaultValue", default=None)
    description: str
    label: str = Field(description="parameter_label, as used in command line")
    unit: Optional[str] = Field(default=None)
    value_set: Optional[List[str]] = Field(alias="valueSet", default=None)
    format_: Optional[str] = Field(alias="format", default=None)
    not_null: bool = Field(
        alias="notNull",
        default=True,
        description="true if the parameter is mandatory",
    )

    @field_validator("data_type")
    @classmethod
    def _data_type_check(cls, val: str) -> str:
        val = val.lower()
        possible_types = [
            "bool",
            "byte",
            "short",
            "int",
            "long",
            "float",
            "double",
            "string",
            "date",
            "polygon",
        ]
        possible_types = [*possible_types, *(f"{t}[]" for t in possible_types)]
        if val not in possible_types:
            msg = f"Value {val} should be one of: {', '.join(possible_types)}"
            raise ValueError(msg)
        return val


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
        description="for executables is VELOCITY",
    )
    variables: Optional[Dict[str, str]] = Field(default=None)
    multi_thread: bool = Field(alias="multiThread", default=False)
    parallelism: Optional[int] = Field(default=None, gt=0)
    visibility: Literal["SYSTEM", "USER", "CONTRIBUTOR"] = Field(default="USER")
    active: bool = Field(default=True)
    component_type: Literal[
        "EXECUTABLE",
        "SCRIPT",
        "AGGREGATE",
        "EXTERNAL",
        "UTILITY",
    ] = Field(alias="componentType", default="EXECUTABLE")
    output_managed: bool = Field(
        alias="outputManaged",
        default=False,
        description=(
            "if true, the output (i.e., file name and location) is managed by TAO; "
            "if false, it is the executable that knows how to create it."
        ),
    )
    parameter_descriptors: List[ParameterDescriptor] = Field(
        alias="parameterDescriptors",
    )
    template_contents: str = Field(
        alias="templatecontents",
        default="",
        description=(
            "parameter labels and value, one per line.\n"
            "Eg.: -source=$source_name\n-parameter_label=$parameter_id\n"
            "-target_name\n$target_name\n"
        ),
    )

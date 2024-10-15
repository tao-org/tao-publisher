# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of TAO Publisher project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TAO component models/schemas.

This module contains the models related to TAO **Processing Components**.
A Processing Component is used to define processing pipelines in TAO,
more precisely **Workflows**.

Note:
    A Processing Component uses a applications from a Toolbox Container to work.
    See the `tao.models.container` module to learn more about containers.
"""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator
from typing_extensions import TypedDict


class _Dimension(TypedDict):
    width: float
    height: float


class _Variable(TypedDict):
    key: str
    value: str


class DataDescriptor(BaseModel):
    """Component data descriptor."""

    format_type: Literal[
        "RASTER",
        "VECTOR",
        "OTHER",
        "FOLDER",
        "JSON",
    ] = Field(alias="formatType", default="RASTER")
    format_name: str | None = Field(alias="formatName", default=None)
    geometry: str | None = Field(default=None)
    crs: str | None = Field(default=None)
    sensor_type: (
        Literal[
            "OPTICAL",
            "RADAR",
            "ALTIMETRIC",
            "ATMOSPHERIC",
            "UNKNOWN",
            "PASSIVE_MICROWAVE",
        ]
        | None
    ) = Field(alias="sensorType", default=None)
    dimension: _Dimension | None = Field(default=None)
    location: Path | None = Field(default=None)


class SourceDescriptor(BaseModel):
    """Component source descriptor."""

    id_: str | None = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")
    constraints: list[str] | None = Field(default=None)
    cardinality: int = Field(
        default=-1,
        ge=-1,
        description="-1 = none, 0 = list, >0 = exact number of items",
    )
    referenced_source_descriptor_id: str | None = Field(
        alias="referencedSourceDescriptorId",
        default=None,
    )


class TargetDescriptor(BaseModel):
    """Component target descriptor."""

    id_: str | None = Field(alias="id", default=None)
    parent_id: str = Field(alias="parentId")
    name: str
    data_descriptor: DataDescriptor = Field(alias="dataDescriptor")
    constraints: list[str] | None = Field(default=None)
    cardinality: int = Field(
        default=0,
        ge=0,
        description="0 = list, >0 = exact number of items, usually 1",
    )
    referenced_target_descriptor_id: str | None = Field(
        alias="referencedTargetDescriptorId",
        default=None,
    )


class ParameterDescriptor(BaseModel):
    """Component parameter descriptor."""

    id_: str = Field(alias="id")
    type_: Literal["REGULAR", "TEMPLATE"] = Field(
        alias="type",
        default="REGULAR",
        description="REGULAR = simple value, TEMPLATE = composed value, "
        "like an XML or JSON.",
    )
    data_type: str = Field(
        alias="dataType",
        description="If polygon, should be WKT, else if date, "
        "the format is in 'format' property.",
    )
    default_value: str | None = Field(alias="defaultValue", default=None)
    description: str
    label: str = Field(description="parameter_label, as used in command line")
    unit: str | None = Field(default=None)
    value_set: list[str] | None = Field(alias="valueSet", default=None)
    format_: str | None = Field(alias="format", default=None)
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

    @field_validator("default_value", mode="before")
    @classmethod
    def _default_value_transform(cls, val: float | str) -> str | None:
        return str(val) if val is not None else None


class Component(BaseModel):
    """Component data as returned by list endpoint."""

    id_: str = Field(alias="id")
    label: str
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    authors: str = Field(default="")
    copyright_: str = Field(alias="copyright", default="")
    node_affinity: str = Field(alias="nodeAffinity", default="Any")
    container_id: str | None = Field(alias="containerId", default=None)
    visibility: Literal["SYSTEM", "USER", "CONTRIBUTOR"] = Field(default="USER")
    active: bool = Field(default=True)
    component_type: Literal[
        "EXECUTABLE",
        "SCRIPT",
        "AGGREGATE",
        "EXTERNAL",
        "UTILITY",
    ] = Field(alias="componentType", default="EXECUTABLE")
    category: Literal["RASTER", "VECTOR", "OPTICAL", "RADAR", "MISC"] = Field(
        default="RASTER",
    )
    output_managed: bool = Field(
        validation_alias=AliasChoices("outputManaged", "managedOutput"),
        serialization_alias="outputManaged",
        default=False,
        description=(
            "if true, the output (i.e., file name and location) is managed by TAO; "
            "if false, it is the executable that knows how to create it."
        ),
    )
    tags: list[str] | None = Field(default=None)


class ComponentDescriptor(Component):
    """Component descriptor for publish and component as returned by get endpoint."""

    sources: list[SourceDescriptor] = Field(default_factory=list)
    targets: list[TargetDescriptor] = Field(default_factory=list)
    file_location: Path = Field(alias="fileLocation")
    working_directory: Path = Field(alias="workingDirectory")
    template_type: Literal["VELOCITY", "JAVASCRIPT", "XSLT", "JSON"] = Field(
        alias="templateType",
        default="VELOCITY",
        description="for executables is VELOCITY",
    )
    variables: list[_Variable] | None = Field(default=None)
    multi_thread: bool = Field(alias="multiThread", default=False)
    parallelism: int | None = Field(default=None, gt=0)
    owner: str | None = Field(default=None)
    transient: bool | None = Field(default=None)
    parameter_descriptors: list[ParameterDescriptor] = Field(
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

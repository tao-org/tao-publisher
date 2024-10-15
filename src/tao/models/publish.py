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

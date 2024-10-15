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

"""Core functionalities.

This module contains functions used for publication, but which are not directly
linked to the TAO API. It is more our management on the client side of the publication,
which is why they are not in `tao.api` which has for intended purpose to be an
interface of the TAO API.

It is here that initialization and reading of a publish file is defined.
"""

import uuid
from pathlib import Path

from pydantic import ValidationError

from tao.exceptions import PublishDefinitionError
from tao.models.component import (
    ComponentDescriptor,
    DataDescriptor,
    ParameterDescriptor,
    SourceDescriptor,
    TargetDescriptor,
)
from tao.models.container import Application, ContainerDescriptor
from tao.models.publish import PublishSpec
from tao.utils.file import parse_file, write_file
from tao.utils.http import slugify


def read_publish_file(file_path: Path) -> PublishSpec:
    """Read publish spec from file.

    Raises:
        FileNotFoundError:
            file_path do not point to an existing file.
        tao.exceptions.PublishDefinitionError:
            file do not define a valid publication request.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    try:
        return PublishSpec(**parse_file(file_path))
    except ValidationError as err:
        msg = "Validation failed.\n"
        raise PublishDefinitionError(msg, validation_error=err) from err


def init_publish_file(name: str, path: Path, file_format: str) -> Path:
    """Init publish spec file with default values and structure.

    Raises:
        FileExistsError:
            file_path point to an existing publish file, cannot overwrite.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
    """
    file_format = file_format.lower()
    file_name = f"{slugify(name)}.{file_format}"
    file_path = path / file_name

    publish_spec = _create_example_publish_spec(name)
    publish_spec_data = publish_spec.model_dump(mode="json", by_alias=True)
    write_file(file_path, publish_spec_data)

    return file_path


def _create_example_publish_spec(name: str) -> PublishSpec:
    container_id = str(uuid.uuid4())
    example_app = Path("example.py")
    example_app_id = "example-app"
    return PublishSpec(
        name=name,
        description="Description of your Toolbox container",
        containerLogo=Path("logo.png"),
        container=ContainerDescriptor(
            id=container_id,
            name=name,
            description="Description of your docker container",
            applications=[
                Application(
                    path=example_app,
                    name=example_app_id,
                    memoryRequirements=4096,
                ),
            ],
        ),
        components=[
            ComponentDescriptor(
                id=example_app_id,
                label="Example app",
                description="Application example",
                sources=[
                    SourceDescriptor(
                        parentId=example_app_id,
                        name="input",
                        cardinality=1,
                        dataDescriptor=DataDescriptor(
                            formatType="RASTER",
                        ),
                    ),
                ],
                targets=[
                    TargetDescriptor(
                        parentId=example_app_id,
                        name="output",
                        dataDescriptor=DataDescriptor(
                            formatType="RASTER",
                            location=Path("output_factorial"),
                        ),
                    ),
                ],
                containerId=container_id,
                fileLocation=example_app,
                workingDirectory=(Path()),
                parameterDescriptors=[
                    ParameterDescriptor(
                        id="myParam",
                        type="REGULAR",
                        dataType="string",
                        defaultValue="default-string-value",
                        description="Parameter of example.py",
                        label="MyParam",
                    ),
                ],
            ),
        ],
        dockerFiles=[Path("Dockerfile"), example_app],
        auxiliaryFiles=[],
    )

"""Core functionalities."""

import uuid
from pathlib import Path

from pydantic import ValidationError

from tao.exceptions import ContainerDefinitionError
from tao.models.component import (
    ComponentDescriptor,
    DataDescriptor,
    ParameterDescriptor,
    SourceDescriptor,
    TargetDescriptor,
)
from tao.models.container import Application, ContainerDescriptor, ContainerSpec
from tao.utils.file import parse_file, write_file
from tao.utils.http import slugify


def read_container_file(file_path: Path) -> ContainerSpec:
    """Read container spec from file.

    Raises:
        FileNotFoundError: file_path do not point to an existing file.
        tao.exceptions.ContainerDefinitionError:
            file do not define a valid container.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    try:
        return ContainerSpec(**parse_file(file_path))
    except ValidationError as err:
        raise ContainerDefinitionError(err) from err


def init_container_file(container_name: str, path: Path, file_format: str) -> Path:
    """Create container spec file.

    Raises:
        FileExistsError:
            file_path point to an existing container file, cannot overwrite.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
    """
    file_format = file_format.lower()
    file_name = f"{slugify(container_name)}.{file_format}"
    file_path = path / file_name

    container_spec = _create_example_container_spec(container_name)
    container_spec_data = container_spec.model_dump(mode="json", by_alias=True)
    write_file(file_path, container_spec_data)

    return file_path


def _create_example_container_spec(container_name: str) -> ContainerSpec:
    container_id = str(uuid.uuid4())
    example_app = Path("example.py")
    example_app_id = "example-app"
    return ContainerSpec(
        name=container_name,
        description="Description of your Toolbox container",
        containerLogo=Path("logo.png"),
        container=ContainerDescriptor(
            id=container_id,
            name=container_name,
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

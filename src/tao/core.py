"""Core functionalities."""

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
        FileNotFoundError: file_path do not point to an existing file.
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
    """Create publish spec file.

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

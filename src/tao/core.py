"""Core functionalities."""

import uuid
from pathlib import Path

from tao.models.component import ComponentDescriptor, ParameterDescriptor
from tao.models.container import Application, ContainerDescriptor, ContainerSpec
from tao.utils.file import parse_file, write_file
from tao.utils.http import slugify


def read_container_file(file_path: Path) -> ContainerSpec:
    """Read container spec from file."""
    return ContainerSpec(**parse_file(file_path))


def init_container_file(container_name: str, path: Path, file_format: str) -> Path:
    """Create container spec file."""
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
                    name="example-app",
                    memoryRequirements=4096,
                ),
            ],
        ),
        components=[
            ComponentDescriptor(
                id="example-app",
                label="Example app",
                description="Application example",
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

"""Container-related API definitions."""


import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tao.exceptions import RequestResponseError
from tao.logging import get_logger
from tao.models.container import Container, ContainerSpec
from tao.utils.http import SerializedFile, serialize_file, serialize_files

from ._base import ServiceAPI

logger = get_logger()


class ContainerAPI(ServiceAPI):
    """Container API client."""

    __api__ = "/docker"

    class SortDirection(str, Enum):
        """Available sort options."""

        ASC = "ASC"
        DESC = "DESC"

    def list(  ## noqa: A003
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by_field: Optional[str] = None,
        sort_direction: Optional[SortDirection] = None,
    ) -> List[Container]:
        """List containers registered in TAO.

        :raises: :class:`pydantic.ValidationError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        query_params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortByField": sort_by_field,
            "sortDirection": sort_direction.value if sort_direction else None,
        }
        params = {k: str(v) for k, v in query_params.items() if v}
        response = self.client.request("GET", self._path(), params=params)
        data = response.get("data")
        if not isinstance(data, list):
            msg = "Unexpected response, didn't contain a list of containers."
            raise RequestResponseError(msg)
        return [Container(**d) for d in data]

    def get(self, container_id: str) -> Container:
        """Get container description.

        :raises: :class:`pydantic.ValidationError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        response = self.client.request("GET", self._path(f"/{container_id}"))
        data: Dict[str, Any] = response.get("data", {})
        return Container(**data)

    def delete(self, container_id: str) -> None:
        """Delete container.

        :raises: :class:`~tao.exceptions.RequestError`
        """
        self.client.request("DELETE", self._path(f"/{container_id}"))

    def register(self, container_spec: ContainerSpec, ctx_path: Path) -> None:
        """Register new container."""
        data, files = self._prepare_container_register_request(
            container_spec,
            ctx_path=ctx_path,
        )
        logger.debug(f"Container register request\n{data=}\n{files=}")
        response = self.client.request(
            "POST",
            self._path("/register"),
            data=data,
            files=files,
        )

        message = response.get("message", response)
        logger.log(logging.DEBUG if message == response else logging.INFO, message)

    def _prepare_container_register_request(
        self,
        container_spec: ContainerSpec,
        ctx_path: Path,
    ) -> Tuple[Dict[str, Any], List[Tuple[str, SerializedFile]]]:
        data = container_spec.model_dump(
            mode="json",
            by_alias=True,
            exclude={"container_logo", "docker_files", "auxiliary_files"},
        )
        data["containerDescriptor"] = json.dumps(data.pop("container"))
        data["componentDescriptors"] = json.dumps(data.pop("components"))

        files: List[Tuple[str, SerializedFile]] = []

        if container_spec.container_logo:
            logo = serialize_file(
                container_spec.container_logo,
                ctx_path=ctx_path,
            )
            if logo:
                files.append(("containerLogo", logo))

        docker_files = serialize_files(
            container_spec.docker_files,
            ctx_path=ctx_path,
        )
        files.extend(("dockerFiles", f) for f in docker_files)

        auxiliary_files = serialize_files(
            container_spec.auxiliary_files,
            ctx_path=ctx_path,
        )
        files.extend(("auxiliaryFiles", f) for f in auxiliary_files)

        return data, files

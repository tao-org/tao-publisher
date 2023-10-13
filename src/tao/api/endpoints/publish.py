"""Publish API definitions."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from tao.logging import get_logger
from tao.models.publish import PublishSpec
from tao.utils.http import SerializedFile, serialize_file, serialize_files

from ._base import EndpointAPI

logger = get_logger()


class PublishAPI(EndpointAPI):
    """Publish API client."""

    __endpoint__ = "/docker/register"

    def push(self, publish_spec: PublishSpec, ctx_path: Path) -> None:
        """Push new container and components.

        Raises:
            tao.exceptions.RequestError: request error.
        """
        data, files = self._prepare_push_request(
            publish_spec,
            ctx_path=ctx_path,
        )
        logger.debug(f"Publish - push request\n{data=}\n{files=}")

        response = self.client.request("POST", self.url(), data=data, files=files)
        message = response.get("message", response)
        logger.log(logging.DEBUG if message == response else logging.INFO, message)

    def _prepare_push_request(
        self,
        publish_spec: PublishSpec,
        ctx_path: Path,
    ) -> Tuple[Dict[str, Any], List[Tuple[str, SerializedFile]]]:
        data = publish_spec.model_dump(
            mode="json",
            by_alias=True,
            exclude={"container_logo", "docker_files", "auxiliary_files"},
        )
        data["containerDescriptor"] = json.dumps(data.pop("container"))
        data["componentDescriptors"] = json.dumps(data.pop("components"))

        files: List[Tuple[str, SerializedFile]] = []

        if publish_spec.container_logo:
            logo = serialize_file(
                publish_spec.container_logo,
                ctx_path=ctx_path,
            )
            if logo:
                files.append(("containerLogo", logo))

        docker_files = serialize_files(
            publish_spec.docker_files,
            ctx_path=ctx_path,
        )
        files.extend(("dockerFiles", f) for f in docker_files)

        auxiliary_files = serialize_files(
            publish_spec.auxiliary_files,
            ctx_path=ctx_path,
        )
        files.extend(("auxiliaryFiles", f) for f in auxiliary_files)

        return data, files

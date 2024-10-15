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

"""Publication API module."""

import json
import logging
from pathlib import Path
from typing import Any

from tao.exceptions import PublishDefinitionError
from tao.logging import _get_logger
from tao.models.publish import PublishSpec
from tao.utils.http import SerializedFile, serialize_file, serialize_files

from .base import EndpointAPI

logger = _get_logger()


class PublishAPI(EndpointAPI, endpoint="/docker/register", auth=True):
    """Publish API client for toolbox containers and processing components.

    Raises:
        tao.exceptions.ConfigurationError:
            - client's config url is not set.
            - auth required but client's token is not set.
    """

    def push(self, publish_spec: PublishSpec, ctx_path: Path) -> None:
        """Push new container and components.

        Note:
            Don't create a `PublishSpec` manually, use the method
            `tao.core.read_publish_file` to read it from a specification file.

        Raises:
            tao.exceptions.RequestError: request error.
            tao.exceptions.PublishDefinitionError: error in publish file.
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
    ) -> tuple[dict[str, Any], list[tuple[str, SerializedFile]]]:
        data = publish_spec.model_dump(
            mode="json",
            by_alias=True,
            exclude={"container_logo", "docker_files", "auxiliary_files"},
        )
        data["containerDescriptor"] = json.dumps(data.pop("container"))
        data["componentDescriptors"] = json.dumps(data.pop("components"))

        files: list[tuple[str, SerializedFile]] = []

        if publish_spec.container_logo:
            logo = serialize_file(
                publish_spec.container_logo,
                ctx_path=ctx_path,
            )
            if logo:
                files.append(("containerLogo", logo))
            else:
                msg = f"Could not find logo file: {publish_spec.container_logo}"
                raise PublishDefinitionError(msg)

        docker_files = serialize_files(
            publish_spec.docker_files,
            ctx_path=ctx_path,
        )
        if len(docker_files) != len(publish_spec.docker_files):
            msg = f"Missing at least one docker files: {publish_spec.docker_files}"
            raise PublishDefinitionError(msg)
        files.extend(("dockerFiles", f) for f in docker_files)

        auxiliary_files = serialize_files(
            publish_spec.auxiliary_files,
            ctx_path=ctx_path,
        )
        if len(auxiliary_files) != len(publish_spec.auxiliary_files):
            msg = (
                f"Missing at least one auxiliary files: {publish_spec.auxiliary_files}"
            )
            raise PublishDefinitionError(msg)
        files.extend(("auxiliaryFiles", f) for f in auxiliary_files)

        return data, files

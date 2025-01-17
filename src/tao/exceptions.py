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

"""TAO client/API exceptions."""

from typing import Any

from pydantic import ValidationError
from requests import HTTPError

from tao.utils.http import HTTP_401_UNAUTHORIZED


class ConfigurationError(ValueError):
    """Configuration error."""


class PublishDefinitionError(RuntimeError):
    """Publish definition error."""

    def __init__(
        self,
        reason: str = "",
        validation_error: ValidationError | None = None,
    ) -> None:
        msg = "Publish definition is invalid.\n"
        msg += reason
        if validation_error:
            msg += "Please check the following validation errors:\n\n"
            msg += str(validation_error)
        super().__init__(msg)
        self.validation_error = ValidationError
        self.msg = msg


class SchemasDifferenceError(RuntimeError):
    """Difference in data schemas between TAO client and server."""

    def __init__(self, validation_error: ValidationError) -> None:
        msg = "Server data schemas may differ from our local schemas.\n"
        msg += "Please contact support.\n\n"
        msg += str(validation_error)
        super().__init__(msg)
        self.validation_error = ValidationError
        self.msg = msg


class RequestError(RuntimeError):
    """Request error base class."""


class RequestHTTPError(RequestError):
    """Request HTTP error."""

    def __init__(
        self,
        status_code: int,
        reason: str | None = None,
        http_error: HTTPError | None = None,
    ) -> None:
        if status_code == HTTP_401_UNAUTHORIZED:
            _msg = "Authentication failed.\n"
        else:
            _msg = f"Request failed: HTTP {status_code}"
        if reason:
            _msg += reason
        super().__init__(_msg)
        self.http_error = http_error


class RequestResponseStatusError(RequestError):
    """Request response status error."""

    def __init__(self, response_json: dict[str, Any]) -> None:
        status = response_json.get("status", "UNKNOWN")
        msg = response_json.get("message", f"Request status: {status}")
        super().__init__(msg)


class RequestResponseError(RequestError):
    """Request response error."""


class LoginError(RequestResponseError):
    """Login error."""

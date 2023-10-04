"""TAO API client module."""

from typing import Any, Optional, cast

import requests

from tao.config import Config
from tao.exceptions import (
    ConfigurationError,
    LoginError,
    RequestHTTPError,
    RequestResponseError,
    RequestResponseStatusError,
)
from tao.logging import get_logger
from tao.utils.http import HTTP_401_UNAUTHORIZED

logger = get_logger()


class APIClient:
    """TAO API Client.

    :raises: :class:`~tao.exceptions.ConfigurationError`
    """

    def __init__(self, config: Config) -> None:
        if not config.url:
            raise ConfigurationError(field="URL")

        self.token = config.token
        self.api_url = config.url.rstrip("/")

    def login(self, username: str, password: str) -> str:
        """Login user and retrieve auth token.

        :raises: :class:`~tao.exceptions.LoginError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        response = self.request(
            "POST",
            "/auth/login",
            data={"username": username, "password": password},
        )
        data = response.get("data")

        if isinstance(data, dict) and "authToken" in data:
            self.token = data["authToken"]
            return cast(str, self.token)

        logger.debug(f"Login data: {data}")
        msg = "Login response missing authToken"
        raise LoginError(msg)

    def request(
        self,
        method: str,
        api_path: str,
        data: Optional[Any] = None,  ## noqa: ANN401
    ) -> Any:  ## noqa: ANN401
        """Send request to TAO API.

        :raises: :class:`~tao.exceptions.RequestHTTPError`
        :raises: :class:`~tao.exceptions.RequestResponseError`
        :raises: :class:`~tao.exceptions.RequestResponseStatusError`
        """
        headers = {}
        if self.token:
            headers["X-Auth-Token"] = self.token
        response = requests.request(
            method=method,
            url=f"{self.api_url}/{api_path.lstrip('/')}",
            headers=headers,
            data=data,
            timeout=30,
        )
        try:
            response.raise_for_status()
            response_json = response.json()
            if isinstance(response_json, dict):
                status = response_json.get("status")
                if status == "SUCCEEDED":
                    return response_json
                raise RequestResponseStatusError(response_json)
            logger.debug(f'Response content: "{response.text}"')
            msg = "Unexpected server response, JSON is malformed."
            raise RequestResponseError(msg)
        except requests.JSONDecodeError as err:
            logger.debug(f'Response content: "{response.text}"')
            msg = "Unexpected server response, expected JSON format."
            raise RequestResponseError(msg) from err
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_401_UNAUTHORIZED:
                reason = "Please verify your username and password."
            else:
                reason = None
            raise RequestHTTPError(
                err.response.status_code,
                reason=reason,
                http_error=err,
            ) from err

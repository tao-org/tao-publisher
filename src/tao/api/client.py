"""API client module."""

from typing import Any, Dict, Optional, cast

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
from tao.utils.http import HTTP_401_UNAUTHORIZED, HttpMethodName

logger = get_logger()


class APIClient:
    """TAO API Client.

    Direct API client to the TAO API. Serves as a basic python interface.
    With the `request` method you can send any requests you desire
    to the TAO API. The `login` method manages authentication.

    For specific operations, with easy data/error handling, use the appropriate
    endpoints API classes in the `tao.api.endpoints` package.

    Parameters:
        config: config object, default config will be used if not provided.

    Raises:
        tao.exceptions.ConfigurationError: config url is not set.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        if not config:
            config = Config()

        if not config.url:
            msg = "URL not configured correctly."
            raise ConfigurationError(msg)

        self.api_url = config.url.rstrip("/")
        self.user = config.user
        self.token = config.token

    def is_authenticated(self) -> bool:
        """Returns True if API token is set, False otherwise."""
        return self.token is not None

    def login(self, password: str, username: Optional[str] = None) -> str:
        """Login user and retrieve auth token.

        Raises:
            tao.exceptions.RequestError: request error.
        """
        username = username if username else self.user
        try:
            response = self.request(
                "POST",
                "/auth/login",
                data={"username": username, "password": password},
            )
        except RequestResponseError as err:
            msg = "Authentication failed.\n"
            msg += "Please verify your username and password."
            raise LoginError(msg) from err

        data = response.get("data")
        if isinstance(data, dict) and "authToken" in data:
            self.token = cast(str, data["authToken"])
            return self.token

        logger.debug(f"Login data: {data}")
        msg = 'Login response missing "authToken".'
        raise LoginError(msg)

    def request(
        self,
        method: HttpMethodName,
        api_path: str,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,  ## noqa: ANN401
        files: Optional[Any] = None,  ## noqa: ANN401
    ) -> Dict[str, Any]:
        """Send request to TAO API.

        Raises:
            tao.exceptions.RequestError: request error.
        """
        headers = {}
        if self.token:
            headers["X-Auth-Token"] = self.token

        response = requests.request(
            method=method,
            url=f"{self.api_url}/{api_path.lstrip('/')}",
            params=params,
            headers=headers,
            data=data,
            files=files,
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

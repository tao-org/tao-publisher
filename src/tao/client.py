"""TAO API client module."""

from typing import Any, Optional, cast

import requests

from tao.config import Config
from tao.logging import get_logger
from tao.utils.http import HTTP_401_UNAUTHORIZED

logger = get_logger()


class APIClient:
    """TAO API Client."""

    def __init__(self, config: Config) -> None:
        if not config.url:
            msg = "URL not configured"
            raise ValueError(msg)

        self.token = config.token
        self.api_url = config.url.rstrip("/")

    def login(self, username: str, password: str) -> str:
        """Login user and retrieve auth token."""
        data = self.request(
            "POST",
            "/auth/login",
            data={"username": username, "password": password},
        )

        if isinstance(data, dict) and "authToken" in data:
            self.token = data["authToken"]
            return cast(str, self.token)

        logger.debug(f"Login data: {data}")
        msg = "Login response missing authToken"
        raise RuntimeError(msg)

    def request(
        self,
        method: str,
        api_path: str,
        data: Optional[Any] = None,  ## noqa: ANN401
    ) -> Any:  ## noqa: ANN401
        """Send request to TAO API."""
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
                if status == "SUCCEEDED" and "data" in response_json:
                    return response_json["data"]
            logger.debug(f"Response content: {response.content.decode()}")
            msg = "Unexpected server response, JSON is malformed."
            raise RuntimeError(msg)
        except requests.JSONDecodeError as err:
            msg += "Unexpected server response, expected JSON format."
            raise RuntimeError(msg) from err
        except requests.HTTPError as err:
            if err.response.status_code == HTTP_401_UNAUTHORIZED:
                msg = "Authentication failed.\n"
                msg += "Please verify your username and password."
            else:
                msg = "Request failed.\n"
                msg += f"HTTP {err.response.status_code}"
            raise RuntimeError(msg) from err

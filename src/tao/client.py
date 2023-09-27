"""TAO API client module."""

from typing import cast

import requests

from tao.config import Config
from tao.logging import get_logger

logger = get_logger()


class TaoApiClient:
    """TAO API Client."""

    def __init__(self, config: Config) -> None:
        if not config.url:
            msg = "URL not configured"
            raise ValueError(msg)

        self.config = config
        self.api_url = config.url.rstrip("/")

    def login(self, username: str, password: str) -> str:
        """Login user and retrieve auth token."""
        response = requests.post(
            url=f"{self.api_url}/auth/login",
            data={"username": username, "password": password},
            timeout=30,
        )
        try:
            response_json = response.json()
            if isinstance(response_json, dict) and "data" in response_json:
                data = response_json["data"]
                if isinstance(data, dict) and "authToken" in data:
                    return cast(str, data["authToken"])
            msg = "Authentication failed.\n"
            msg += "Unexpected server response."
            raise ValueError(msg)
        except requests.JSONDecodeError as err:
            msg = "Authentication failed.\n"
            msg += "Please verify your username and password."
            raise ValueError(msg) from err

"""TAO client/API exceptions."""

from typing import Any, Dict, Optional

from requests import HTTPError

from tao.utils.http import HTTP_401_UNAUTHORIZED


class ConfigurationError(ValueError):
    """Configuration error."""

    def __init__(self, field: str) -> None:
        super().__init__(f"{field} not configured correctly.")


class RequestError(RuntimeError):
    """Request error base class."""


class RequestHTTPError(RequestError):
    """Request HTTP error."""

    def __init__(
        self,
        status_code: int,
        reason: Optional[str] = None,
        http_error: Optional[HTTPError] = None,
    ) -> None:
        if status_code == HTTP_401_UNAUTHORIZED:
            _msg = "Authentication failed.\n"
        else:
            _msg = f"Request failed: HTTP {status_code}"
        if reason:
            _msg += reason
        super().__init__(_msg)
        self.http_error = http_error


class RequestResponseError(RequestError):
    """Request response error."""


class RequestResponseStatusError(RequestError):
    """Request response status error."""

    def __init__(self, response_json: Dict[str, Any]) -> None:
        status = response_json.get("status", "UNKNOWN")
        msg = response_json.get("message", f"Request status: {status}")
        super().__init__(msg)


class LoginError(RequestResponseError):
    """Login error."""

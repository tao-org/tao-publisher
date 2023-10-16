from typing import Optional

from tao.api.client import APIClient
from tao.exceptions import ConfigurationError


class EndpointAPI:
    """Endpoint API client base class.

    Raises:
        tao.exceptions.ConfigurationError:
            client's config url is not set.
            or
            auth required but client's token is not set.
    """

    __endpoint__ = "/"
    __auth__ = True

    def __init__(self, client: Optional[APIClient] = None) -> None:
        if not client:
            client = APIClient()

        if self.is_auth_required() and not client.is_authenticated():
            msg = "Authentication is required but API client's "
            msg += "config is missing an API Token."
            raise ConfigurationError(msg)

        self.client = client

    def __init_subclass__(cls, endpoint: str = "/", auth: bool = False) -> None:
        super().__init_subclass__()
        cls.__endpoint__ = endpoint
        cls.__auth__ = auth

    @property
    def endpoint(self) -> str:
        return self.__endpoint__

    def is_auth_required(self) -> bool:
        return self.__auth__

    def url(self, path: str = "", /) -> str:
        return f"{self.endpoint.rstrip('/')}/{path.lstrip('/')}"

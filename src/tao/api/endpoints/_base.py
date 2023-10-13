from typing import Optional

from tao.api.client import APIClient


class EndpointAPI:
    """Endpoint API client base class.

    Raises:
        tao.exceptions.ConfigurationError: client's config url is not set.
    """

    __endpoint__ = "/"

    def __init__(self, client: Optional[APIClient] = None) -> None:
        if not client:
            client = APIClient()

        self.client = client

    def url(self, path: str = "", /) -> str:
        return f"{self.__endpoint__.rstrip('/')}/{path.lstrip('/')}"

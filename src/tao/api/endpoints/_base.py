from tao.api.client import APIClient


class EndpointAPI:
    """Endpoint API client base class."""

    __endpoint__ = "/"

    def __init__(self, client: APIClient) -> None:
        self.client = client

    def url(self, path: str = "", /) -> str:
        return f"{self.__endpoint__.rstrip('/')}/{path.lstrip('/')}"

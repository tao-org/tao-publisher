from tao.api.client import APIClient


class ServiceAPI:
    __api__ = "/"

    def __init__(self, client: APIClient) -> None:
        self.client = client

    def url(self, path: str = "", /) -> str:
        return f"{self.__api__.rstrip('/')}/{path.lstrip('/')}"

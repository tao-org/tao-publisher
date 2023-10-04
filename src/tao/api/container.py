"""Container-related API definitions."""


from typing import List

from tao.exceptions import RequestResponseError
from tao.models.container import Container

from ._base import ServiceAPI


class ContainerAPI(ServiceAPI):
    """Container API client."""

    __api__ = "/docker"

    def list_all(self) -> List[Container]:
        """List containers registered in TAO.

        :raises: :class:`pydantic.ValidationError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        response = self.client.request("GET", self._path())
        data = response.get("data")
        if not isinstance(data, list):
            msg = "Unexpected response, didn't contain a list of containers."
            raise RequestResponseError(msg)
        return [Container(**d) for d in data]

    def get(self, container_id: str) -> Container:
        """Get container description.

        :raises: :class:`pydantic.ValidationError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        response = self.client.request("GET", self._path(f"/{container_id}"))
        data = response.get("data")
        return Container(**data)

    def delete(self, container_id: str) -> None:
        """Delete container.

        :raises: :class:`~tao.exceptions.RequestError`
        """
        self.client.request("DELETE", self._path(f"/{container_id}"))

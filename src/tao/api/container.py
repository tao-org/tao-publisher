"""Container-related API definitions."""


from typing import List

from tao.models.container import ContainerDescription

from ._base import ServiceAPI


class ContainerAPI(ServiceAPI):
    """Container API client."""

    __api__ = "/docker"

    def list_all(self) -> List[ContainerDescription]:
        """List containers registered in TAO."""
        response = self.client.request("GET", self._path())
        data = response.get("data")
        if not isinstance(data, list):
            msg = "Unexpected response, didn't contain a list of containers."
            raise TypeError(
                msg,
            )
        return [ContainerDescription(**d) for d in data]

    def get(self, container_id: str) -> ContainerDescription:
        """Get container description."""
        response = self.client.request("GET", self._path(f"/{container_id}"))
        data = response.get("data")
        return ContainerDescription(**data)

    def delete(self, container_id: str) -> None:
        """Delete container."""
        self.client.request("DELETE", self._path(f"/{container_id}"))

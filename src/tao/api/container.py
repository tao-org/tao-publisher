"""Container-related API definitions."""


from typing import List

from tao.models.container import ContainerDescription

from ._base import ServiceAPI


class ContainerAPI(ServiceAPI):
    """Container API client."""

    __api__ = "/docker"

    def list_all(self) -> List[ContainerDescription]:
        """List containers registered in TAO."""
        data = self.client.request("GET", self._path())
        if not isinstance(data, list):
            msg = "Unexpected response, didn't contain a list of containers."
            raise TypeError(
                msg,
            )
        return [ContainerDescription(**d) for d in data]

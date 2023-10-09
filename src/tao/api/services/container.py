"""Container-related API definitions."""


from enum import Enum
from typing import List, Optional

from tao.exceptions import RequestResponseError
from tao.models.container import Container

from ._base import ServiceAPI


class ContainerAPI(ServiceAPI):
    """Container API client."""

    __api__ = "/docker"

    class SortDirection(str, Enum):
        """Available sort options."""

        ASC = "ASC"
        DESC = "DESC"

    def list(  ## noqa: A003
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by_field: Optional[str] = None,
        sort_direction: Optional[SortDirection] = None,
    ) -> List[Container]:
        """List containers registered in TAO.

        :raises: :class:`pydantic.ValidationError`
        :raises: :class:`~tao.exceptions.RequestError`
        """
        query_params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortByField": sort_by_field,
            "sortDirection": sort_direction.value if sort_direction else None,
        }
        params = {k: str(v) for k, v in query_params.items() if v}
        response = self.client.request("GET", self._path(), params=params)
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

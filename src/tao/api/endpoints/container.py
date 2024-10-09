"""Container-related API module."""

from enum import Enum
from typing import Any

from pydantic import ValidationError

from tao.exceptions import RequestResponseError, SchemasDifferenceError
from tao.logging import _get_logger
from tao.models.container import Container

from .base import EndpointAPI

logger = _get_logger()


class ContainerAPI(EndpointAPI, endpoint="/docker", auth=True):
    """API client for TAO toolbox containers.

    Raises:
        tao.exceptions.ConfigurationError:
            - client's config url is not set.
            - auth required but client's token is not set.
    """

    class SortDirection(str, Enum):
        """Available sort options."""

        ASC = "ASC"
        DESC = "DESC"

    def list(
        self,
        page_number: int | None = None,
        page_size: int | None = None,
        sort_by_field: str | None = None,
        sort_direction: SortDirection | None = None,
    ) -> list[Container]:
        """List toolbox containers registered in TAO.

        Raises:
            tao.exceptions.RequestError:
                request error.
            tao.exceptions.SchemasDifferenceError:
                local models differs from server response format,
                schemas could have changed.
        """
        if not sort_by_field and (page_number is not None or page_size is not None):
            sort_by_field = "id"
        query_params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortByField": sort_by_field,
            "sortDirection": sort_direction.value if sort_direction else None,
        }
        params = {k: str(v) for k, v in query_params.items() if v}
        response = self.client.request("GET", self.url(), params=params)

        data = response.get("data")
        if not isinstance(data, list):
            msg = "Unexpected response, data didn't contain a list of containers."
            raise RequestResponseError(msg)

        try:
            return [Container(**d) for d in data]
        except TypeError as err:
            msg = "Unexpected response, data didn't contain a list mappings."
            raise RequestResponseError(msg) from err
        except ValidationError as err:
            raise SchemasDifferenceError(err) from err

    def get(self, container_id: str) -> Container:
        """Get toolbox container details.

        Raises:
            tao.exceptions.RequestError:
                request error.
            tao.exceptions.SchemasDifferenceError:
                local models differs from server response format,
                schemas could have changed.
        """
        response = self.client.request("GET", self.url(f"/{container_id}"))
        data: dict[str, Any] = response.get("data", {})
        try:
            return Container(**data)
        except TypeError as err:
            msg = "Unexpected response, data didn't contain a list mappings."
            raise RequestResponseError(msg) from err
        except ValidationError as err:
            raise SchemasDifferenceError(err) from err

    def delete(self, container_id: str) -> None:
        """Delete toolbox container.

        Raises:
            tao.exceptions.RequestError: request error.
        """
        self.client.request("DELETE", self.url(f"/{container_id}"))

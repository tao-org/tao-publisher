"""Component-related API module."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from tao.exceptions import RequestResponseError, SchemasDifferenceError
from tao.logging import get_logger
from tao.models.component import Component, ComponentDescriptor

from .base import EndpointAPI

logger = get_logger()


class ComponentAPI(EndpointAPI, endpoint="/component", auth=True):
    """API client for TAO processing components.

    Raises:
        tao.exceptions.ConfigurationError:
            - client's config url is not set.
            - auth required but client's token is not set.
    """

    class SortDirection(str, Enum):
        """Available sort options."""

        ASC = "ASC"
        DESC = "DESC"

    def list(  ## noqa: A003
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[SortDirection] = None,
    ) -> List[Component]:
        """List processing components registered in TAO.

        Raises:
            tao.exceptions.RequestError:
                request error.
            tao.exceptions.SchemasDifferenceError:
                local models differs from server response format,
                schemas could have changed.
        """
        query_params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortBy": sort_by if sort_by else "id",
            "sortDirection": sort_direction.value if sort_direction else None,
        }
        params = {k: str(v) for k, v in query_params.items() if v}
        response = self.client.request("GET", self.url(), params=params)

        data = response.get("data")
        if not isinstance(data, list):
            msg = "Unexpected response, data didn't contain a list of components."
            raise RequestResponseError(msg)

        try:
            return [Component(**d) for d in data]
        except TypeError as err:
            msg = "Unexpected response, data didn't contain a list mappings."
            raise RequestResponseError(msg) from err
        except ValidationError as err:
            raise SchemasDifferenceError(err) from err

    def get(self, component_id: str) -> ComponentDescriptor:
        """Get processing component details.

        Raises:
            tao.exceptions.RequestError:
                request error.
            tao.exceptions.SchemasDifferenceError:
                local models differs from server response format,
                schemas could have changed.
        """
        response = self.client.request(
            "GET",
            self.url(f"/{component_id}"),
            params={"id": component_id},  # TODO: remove id param when API is fixed
        )
        data: Dict[str, Any] = response.get("data", {})
        try:
            return ComponentDescriptor(**data)
        except TypeError as err:
            msg = "Unexpected response, data didn't contain a list mappings."
            raise RequestResponseError(msg) from err
        except ValidationError as err:
            raise SchemasDifferenceError(err) from err

    def delete(self, component_id: str) -> None:
        """Delete processing component.

        Raises:
            tao.exceptions.RequestError: request error.
        """
        self.client.request("DELETE", self.url(f"/{component_id}"))

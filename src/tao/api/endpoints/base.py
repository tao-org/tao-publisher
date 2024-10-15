# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of TAO Publisher project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Base API endpoint class."""

from tao.api.client import APIClient
from tao.exceptions import ConfigurationError


class EndpointAPI:
    """Endpoint API client base class.

    An endpoint must be configured with two parameters, `endpoint` and `auth`.
    The former corresponds to the endpoint route relative to the TAO API base URL,
    and the latter if authentication is globally required for the endpoint.

    If authentication is globally required, a ConfigurationError can be raised if
    the given config do not have a token set.

    The data is processed and validated with the models in the `tao.models` module.

    Examples:
        Test configs:

        >>> from tao import Config, APIClient
        >>> empty_config = Config(load=False)
        >>> simple_config = Config(load=False, url="https://example.com")
        >>> auth_config = Config(load=False, url="https://example.com", token="")

        Declaration of a simple endpoint:

        >>> class TestAPI(EndpointAPI, endpoint="/test"):
        ...     pass

        Declaration of an endpoint with authentication required:

        >>> class AuthTestAPI(EndpointAPI, endpoint="/test", auth=True):
        ...     pass

        When config is empty you can't instantiate because config url needs
        to be defined.

        >>> api = TestAPI(client=APIClient(config=empty_config))
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        tao.exceptions.ConfigurationError

        No problem otherwise

        >>> api = TestAPI(client=APIClient(config=simple_config))

        When authentication is required, token must be set for config

        >>> api = AuthTestAPI(client=APIClient(config=simple_config))
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        tao.exceptions.ConfigurationError

        With a token set there is no error

        >>> api = AuthTestAPI(client=APIClient(config=auth_config))



    Raises:
        tao.exceptions.ConfigurationError:
            client's config url is not set.
            or
            auth required but client's token is not set.
    """

    __endpoint__ = "/"
    __auth__ = True

    def __init__(self, client: APIClient | None = None) -> None:
        if not client:  # pragma: no cover
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
        """Returns the endpoint path.

        Examples:
            Test config:

            >>> from tao import Config, APIClient
            >>> config = Config(load=False, url="https://example.com")
            >>> client = APIClient(config=config)

            >>> class TestAPI(EndpointAPI, endpoint="/test"):
            ...     pass
            >>> api = TestAPI(client=APIClient(config=config))
            >>> api.endpoint
            '/test'
        """
        return self.__endpoint__

    def is_auth_required(self) -> bool:
        """Returns True if the endpoint is globally requiring authentication.

        Examples:
            Test config:

            >>> from tao import Config, APIClient
            >>> config = Config(load=False, url="https://example.com", token="")
            >>> client = APIClient(config=config)

            No auth required

            >>> class TestAPI(EndpointAPI, auth=False):
            ...     pass
            >>> api = TestAPI(client)
            >>> api.is_auth_required()
            False

            Auth required

            >>> class TestAPI(EndpointAPI, auth=True):
            ...     pass
            >>> api = TestAPI(client)
            >>> api.is_auth_required()
            True
        """
        return self.__auth__

    def url(self, path: str = "", /) -> str:
        """Returns absolute URL path to the API base URL for an endpoint path.

        Examples:
            Test config:

            >>> from tao import Config, APIClient
            >>> config = Config(load=False, url="https://example.com", token="")
            >>> client = APIClient(config=config)

            .url(...) example

            >>> class TestAPI(EndpointAPI, endpoint="/test"):
            ...     pass
            >>> api = TestAPI(client)
            >>> api.url("/something")
            '/test/something'
        """
        return f"{self.endpoint.rstrip('/')}/{path.lstrip('/')}"

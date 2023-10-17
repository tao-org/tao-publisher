"""TAO API package.

This package contains the API client as well as API endpoints.
You could say that everything in this package is the pure interface to the TAO API.

Warning:
    Any "breaking change" in the TAO API could lead to malfunctions.
"""

from .client import APIClient
from .endpoints import ComponentAPI, ContainerAPI, PublishAPI

__all__ = ["APIClient", "ComponentAPI", "ContainerAPI", "PublishAPI"]

"""TAO API endpoints package.

Each API endpoint is a class that represents an API route and the operations
available for that endpoint. They can be with or without authentication.
Each operation corresponds to an HTTP call, which can be GET, POST, DELETE
for a relative sub-route of the endpoint etc...
"""

from .component import ComponentAPI
from .container import ContainerAPI
from .publish import PublishAPI

__all__ = ["ComponentAPI", "ContainerAPI", "PublishAPI"]

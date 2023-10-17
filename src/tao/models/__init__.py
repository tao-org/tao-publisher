"""TAO models package.

This package contains the models corresponding to the TAO API data schemas.
They handle the data validation thanks to the use of Pydantic.

The models are just a way to encapsulate the data returned by the API,
they are used by the endpoints API classes in the package `tao.api.endpoints`.

Warning:
    Any "breaking change" in the TAO API could lead to malfunctions.
"""

from .component import Component, ComponentDescriptor
from .container import Container
from .publish import PublishSpec

__all__ = ["Component", "ComponentDescriptor", "Container", "PublishSpec"]

"""TAO Publisher top-level package.

This python package delivers a CLI and a python API to interact with the TAO API.

Available features:

- List, get, and delete of **Toolbox Containers**.
- List, get, and delete of **Processing Components**.
- Definition of Toolbox Containers and Processing Components with a declarative file,
  and a publish mechanism to register them inside TAO.
"""

from importlib.metadata import PackageNotFoundError, version

from tao.api import APIClient, PublishAPI
from tao.config import Config

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "undefined"


__all__ = ["Config", "APIClient", "PublishAPI"]

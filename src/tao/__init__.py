"""TAO Publisher top-level module."""

from importlib.metadata import PackageNotFoundError, version

from tao.api import APIClient, PublishAPI
from tao.config import Config

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "undefined"


__all__ = ["Config", "APIClient", "PublishAPI"]

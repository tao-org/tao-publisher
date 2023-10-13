"""Configuration for TAO Publisher."""

from base64 import b64decode, b64encode
from pathlib import Path
from typing import Optional, TypedDict, cast

import click
import yaml

from tao.logging import get_logger

CONFIG_FILENAME = "config.yaml"
DEFAULT_CONFIG_DIR = Path(click.get_app_dir(__package__))

logger = get_logger()


class _ConfigDict(TypedDict):
    url: Optional[str]
    token: Optional[str]


class Config:
    """Class containing the project configuration."""

    def __init__(
        self,
        config_dir: Path = DEFAULT_CONFIG_DIR,
    ) -> None:
        self.config_dir = config_dir
        self.config_file = self.config_dir / CONFIG_FILENAME

        conf = self._read()
        conf.setdefault("url", None)
        conf.setdefault("token", None)
        self._conf = conf

    def _read(self) -> _ConfigDict:
        if not self.config_dir.is_dir():
            logger.debug(f"Create dir: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_file.is_file():
            logger.debug(f"Config file not found at: {self.config_file}")
            return _ConfigDict(url=None, token=None)

        logger.debug(f"Read config from: {self.config_file}")
        with self.config_file.open() as file:
            return cast(_ConfigDict, yaml.safe_load(file))

    def write(self) -> None:
        """Write config file."""
        logger.debug(f"Write config to file: {self.config_file}")
        with self.config_file.open("w") as file:
            yaml.dump(self._conf, file, default_flow_style=False)

    @property
    def url(self) -> Optional[str]:
        """TAO API BASE URL."""
        return self._conf["url"]

    @url.setter
    def url(self, val: Optional[str]) -> None:
        """Set config url."""
        self._conf["url"] = val

    @property
    def token(self) -> Optional[str]:
        """TAO user auth token."""
        _token = self._conf["token"]
        if _token:
            _token = b64decode(_token.encode()).decode()
        return _token

    @token.setter
    def token(self, val: Optional[str]) -> None:
        """Save auth informations."""
        if val:
            val = b64encode(val.encode()).decode()
        self._conf["token"] = val

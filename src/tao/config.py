"""Configuration for TAO Publisher."""

from base64 import b64decode, b64encode
from pathlib import Path
from typing import Optional, TypedDict, cast

import click
import yaml

from tao.exceptions import ConfigurationError
from tao.logging import get_logger

_CONFIG_FILENAME = "config.yaml"
_DEFAULT_CONFIG_DIR = Path(click.get_app_dir(__package__))
_DEFAULT_CONFIG_FILE_PATH = _DEFAULT_CONFIG_DIR / _CONFIG_FILENAME

logger = get_logger()


class _ConfigDict(TypedDict):
    url: Optional[str]
    user: Optional[str]
    token: Optional[str]


class Config:
    """Class containing the project configuration.

    Raises:
        tao.exceptions.ConfigurationError: config file content is invalid.
    """

    def __init__(self, file_path: Optional[Path] = None) -> None:
        self._file_path = file_path if file_path else _DEFAULT_CONFIG_FILE_PATH
        self._conf = _ConfigDict(url=None, user=None, token=None)
        self.load()

    def load(self) -> None:
        """Load config file.

        Raises:
            tao.exceptions.ConfigurationError: config file content is invalid.
        """
        if self._file_path.is_file():
            logger.debug(f"Load config from: {self._file_path}")
            try:
                with self._file_path.open() as file:
                    content = cast(_ConfigDict, yaml.safe_load(file))
                    self._conf.update(content)
            except (TypeError, ValueError, yaml.YAMLError) as err:
                msg = f"Config content error:\n\n{err}"
                raise ConfigurationError(msg) from err

            # Ensure keys are at least defined
            self._conf.setdefault("url", None)
            self._conf.setdefault("user", None)
            self._conf.setdefault("token", None)
        else:
            logger.debug(f"Config file not found at: {self._file_path}")

    def write(self) -> None:
        """Write config file."""
        _config_dir = self._file_path.parent
        if not _config_dir.is_dir():
            logger.debug(f"Create config dir: {_config_dir}")
            _config_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Write config to file: {self._file_path}")
        with self._file_path.open("w") as file:
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
    def user(self) -> Optional[str]:
        """User."""
        return self._conf["user"]

    @user.setter
    def user(self, val: Optional[str]) -> None:
        """Set config user."""
        self._conf["user"] = val

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

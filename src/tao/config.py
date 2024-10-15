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

"""Configuration for TAO Publisher."""

from base64 import b64decode, b64encode
from pathlib import Path
from typing import TypedDict, cast

import click
import yaml

from tao.exceptions import ConfigurationError
from tao.logging import _get_logger

_CONFIG_FILENAME = "config.yaml"
_DEFAULT_CONFIG_DIR = Path(click.get_app_dir(__package__))
_DEFAULT_CONFIG_FILE_PATH = _DEFAULT_CONFIG_DIR / _CONFIG_FILENAME

logger = _get_logger()


class _ConfigDict(TypedDict):
    url: str | None
    user: str | None
    token: str | None


class Config:
    """Manage the configuration.

    By default read config file.

    Parameters:
        file_path:
            path to the config file. Defaults to _~/.config/tao/config.yaml_
            if not given.
        load: whether to load the config file of not.
        url: default url to use, may be overwritten by config file content.
        user: default user to use, may be overwritten by config file content.
        token: default token to use, may be overwritten by config file content.

    Note:
        If you do not wish to load the file with `load=False` don't forget
        to at least set your config's `url` and `token`.

    Raises:
        tao.exceptions.ConfigurationError: config file content is invalid.
    """

    def __init__(
        self,
        file_path: Path | None = None,
        load: bool = True,
        url: str | None = None,
        user: str | None = None,
        token: str | None = None,
    ) -> None:
        self._file_path = file_path if file_path else _DEFAULT_CONFIG_FILE_PATH
        self._conf = _ConfigDict(url=None, user=None, token=None)

        self.url = url
        self.user = user
        self.token = token

        if load:
            self.load()

    def load(self) -> None:
        """Load config from config file.

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

    def save(self) -> None:
        """Save config to config file."""
        _config_dir = self._file_path.parent
        if not _config_dir.is_dir():
            logger.debug(f"Create config dir: {_config_dir}")
            _config_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Write config to file: {self._file_path}")
        with self._file_path.open("w") as file:
            yaml.dump(self._conf, file, default_flow_style=False)

    @property
    def url(self) -> str | None:
        """TAO API BASE URL."""
        return self._conf["url"]

    @url.setter
    def url(self, val: str | None) -> None:
        """Set config url."""
        self._conf["url"] = val

    @property
    def user(self) -> str | None:
        """User."""
        return self._conf["user"]

    @user.setter
    def user(self, val: str | None) -> None:
        """Set config user."""
        self._conf["user"] = val

    @property
    def token(self) -> str | None:
        """TAO user auth token."""
        _token = self._conf["token"]
        if _token:
            _token = b64decode(_token.encode()).decode()
        return _token

    @token.setter
    def token(self, val: str | None) -> None:
        """Save auth informations."""
        if val:
            val = b64encode(val.encode()).decode()
        self._conf["token"] = val

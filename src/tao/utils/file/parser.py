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

"""File parsers utilities.

This modules contains configuration-parsing function utilities, with a main
`parse_file` function that allows you to retrieve a file's content as a `dict` with
`str` as top-level keys. Multiple file extensions are supported, and support for other
can be added in the future.

Currently support parsing for YAML (`.yml`, `.yaml`), and JSON (`.json`).
"""

import json
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

import yaml

from .exceptions import FileContentError, FileExtensionInvalidError

FileContent = dict[str, Any]
ParserFunc = Callable[[Path], FileContent]

_PARSERS: dict[ParserFunc, list[str]] = {}


def get_valid_parsable_extensions() -> list[str]:
    """Get all extensions with an existing parser."""
    extensions = set()
    for _extensions in _PARSERS.values():
        extensions.update(_extensions)
    return list(extensions)


def get_parser(file_ext: str, /) -> ParserFunc | None:
    """Get parser for config files with the corresponding file extension."""
    for parser_func, extensions in _PARSERS.items():
        if file_ext in extensions:
            return parser_func
    return None


def parse_file(file_path: Path, /) -> FileContent:
    """Parse a configuration file.

    The configuration file  content is returned as a `dict` with `str` keys.

    Raises:
        FileNotFoundError:
            file_path do not point to an existing file.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    if parser := get_parser(file_path.suffix):
        return parser(file_path)
    msg = f"Invalid file extension: {file_path}"
    raise FileExtensionInvalidError(msg)


def _register_parser(*, extensions: list[str]) -> Callable[[ParserFunc], ParserFunc]:
    def decorator(parser_func: ParserFunc) -> ParserFunc:
        @wraps(parser_func)
        def wrapper(file_path: Path, /) -> FileContent:
            if not file_path.is_file():
                msg = f"File not found: {file_path}"
                raise FileNotFoundError(msg)
            if file_path.suffix not in extensions:
                msg = f"Invalid file extension: {file_path}"
                raise FileExtensionInvalidError(msg)
            return parser_func(file_path)

        _PARSERS[wrapper] = extensions
        return wrapper

    return decorator


@_register_parser(extensions=[".yaml", ".yml"])
def _parse_yaml(file_path: Path, /) -> FileContent:
    try:
        with file_path.open() as file:
            content = yaml.safe_load(file)
        return _parse_content(content)
    except (TypeError, yaml.YAMLError) as err:
        msg = f"Invalid YAML file: {file_path}\n"
        msg += "Please check for syntax errors."
        raise FileContentError(msg) from err


@_register_parser(extensions=[".json"])
def _parse_json(file_path: Path, /) -> FileContent:
    try:
        with file_path.open() as file:
            content = json.load(file)
        return _parse_content(content)
    except json.JSONDecodeError as err:
        msg = f"Invalid JSON file: {file_path}\n"
        msg += "Please check for syntax errors."
        raise FileContentError(msg) from err


def _parse_content(
    content: list[Any] | dict[Any, Any] | None,
) -> FileContent:
    content_dict = {}
    if isinstance(content, dict):
        content_dict = content
    if isinstance(content, list):
        content_dict = {"values": content}
    for k in content_dict:
        if not isinstance(k, str):
            msg = f"Expected all keys to be {str}: {content_dict}"
            raise FileContentError(msg)
    return content_dict

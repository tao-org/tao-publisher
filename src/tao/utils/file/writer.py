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

"""File writers utilities.

This module contains the configuration-writing function utilities, with a main
`write_file` function that allows you to write a configuration in a file from a `dict`
with `str` keys. Multiple file extensions are supported, and support for other
can be added in the future.

Currently support writing to YAML (`.yml`, `.yaml`), and JSON (`.json`).
"""

import json
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

import yaml

from .exceptions import FileExtensionInvalidError

FileContent = dict[str, Any]
WriterFunc = Callable[[Path, FileContent], None]

_WRITERS: dict[WriterFunc, list[str]] = {}


def get_valid_writable_extensions() -> list[str]:
    """Get all extensions with an existing writer."""
    extensions = set()
    for _extensions in _WRITERS.values():
        extensions.update(_extensions)
    return list(extensions)


def get_writer(file_ext: str, /) -> WriterFunc | None:
    """Get writer for config files with the corresponding file extension."""
    for writer_func, extensions in _WRITERS.items():
        if file_ext in extensions:
            return writer_func
    return None


def write_file(file_path: Path, /, data: FileContent) -> None:
    """Write data to configuration file.

    The configuration file content is a `dict` with `str` keys.

    Warning:
        If your data contains custom python objects, you may encounter some errors.
        It is recommended to transform everything to python builtins types.

    Raises:
        FileExistsError:
            file already exists at `file_path`.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
    """
    if writer := get_writer(file_path.suffix):
        return writer(file_path, data)
    msg = f"Invalid file extension: {file_path}"
    raise FileExtensionInvalidError(msg)


def _register_writer(*, extensions: list[str]) -> Callable[[WriterFunc], WriterFunc]:
    def decorator(writer_func: WriterFunc) -> WriterFunc:
        @wraps(writer_func)
        def wrapper(file_path: Path, /, data: FileContent) -> None:
            if file_path.exists():
                msg = f"File already exists: {file_path}"
                raise FileExistsError(msg)
            if file_path.suffix not in extensions:
                msg = f"Invalid file extension: {file_path}"
                raise FileExtensionInvalidError(msg)
            return writer_func(file_path, data)

        _WRITERS[wrapper] = extensions
        return wrapper

    return decorator


@_register_writer(extensions=[".yaml", ".yml"])
def _write_yaml(file_path: Path, /, data: FileContent) -> None:
    with file_path.open("w") as file:
        yaml.dump(data, file, sort_keys=False)


@_register_writer(extensions=[".json"])
def _write_json(file_path: Path, /, data: FileContent) -> None:
    with file_path.open("w") as file:
        json.dump(data, file, indent=2, sort_keys=False)

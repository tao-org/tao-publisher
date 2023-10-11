"""File writers utilities."""

import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from .exceptions import FileExtensionInvalidError

FileContent = Dict[str, Any]
WriterFunc = Callable[[Path, FileContent], None]

_WRITERS: Dict[WriterFunc, List[str]] = {}


def get_valid_writable_extensions() -> List[str]:
    """Get all extensions with existing writer."""
    extensions = set()
    for _extensions in _WRITERS.values():
        extensions.update(_extensions)
    return list(extensions)


def register_writer(*, extensions: List[str]) -> Callable[[WriterFunc], WriterFunc]:
    """Writer decorator."""

    def decorator(writer_func: WriterFunc) -> WriterFunc:
        """Allow optional arguments for decorator."""

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


def write_file(file_path: Path, /, data: FileContent) -> None:
    """Write data to file.

    :raises: :class:`FileExistsError`
    :raises: :class:`~tao.utils.file.exceptions.FileExtensionInvalidError`
    """
    if writer := get_writer(file_path.suffix):
        return writer(file_path, data)
    msg = f"Invalid file extension: {file_path}"
    raise FileExtensionInvalidError(msg)


def get_writer(file_ext: str, /) -> Optional[WriterFunc]:
    """Get writer for files with corresponding file extension."""
    for writer_func, extensions in _WRITERS.items():
        if file_ext in extensions:
            return writer_func
    return None


@register_writer(extensions=[".yaml", ".yml"])
def write_yaml(file_path: Path, /, data: FileContent) -> None:
    """YAML document writer.

    :raises: :class:`FileExistsError`
    :raises: :class:`~tao.utils.file.exceptions.FileExtensionInvalidError`
    """
    with file_path.open("w") as file:
        yaml.dump(data, file, sort_keys=False)


@register_writer(extensions=[".json"])
def write_json(file_path: Path, /, data: FileContent) -> None:
    """JSON document writer.

    :raises: :class:`FileExistsError`
    :raises: :class:`~tao.utils.file.exceptions.FileExtensionInvalidError`
    """
    with file_path.open("w") as file:
        json.dump(data, file, indent=2, sort_keys=False)

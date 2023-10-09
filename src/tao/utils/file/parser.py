"""File parsers utilities."""

import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml

from .exceptions import FileExtensionInvalidError

FileContent = Dict[str, Any]
ParserFunc = Callable[[Path], FileContent]

_PARSERS: Dict[ParserFunc, List[str]] = {}


def get_valid_parsable_extensions() -> List[str]:
    """Get all extensions with existing parser."""
    extension_set = set()
    for _extensions in _PARSERS.values():
        extension_set.update(_extensions)
    return list(extension_set)


def register_parser(extensions: List[str]) -> Callable[[ParserFunc], ParserFunc]:
    """Parser decorator."""

    def decorator(parser_func: ParserFunc) -> ParserFunc:
        """Allow optional arguments for decorator."""

        @wraps(parser_func)
        def wrapper(file_path: Path) -> FileContent:
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


def parse_file(file_path: Path) -> FileContent:
    """Parse file."""
    if parser := get_parser(file_path.suffix):
        return parser(file_path)
    msg = f"Invalid file extension: {file_path}"
    raise FileExtensionInvalidError(msg)


def get_parser(file_ext: str) -> Optional[ParserFunc]:
    """Get parser for files with corresponding file extension."""
    for parser_func, extensions in _PARSERS.items():
        if file_ext in extensions:
            return parser_func
    return None


@register_parser(extensions=[".yaml", ".yml"])
def parse_yaml(file_path: Path) -> FileContent:
    """YAML document parser."""
    with file_path.open() as file:
        content = yaml.safe_load(file)
    return _parse_content(content)


@register_parser(extensions=[".json"])
def parse_json(file_path: Path) -> FileContent:
    """JSON document parser."""
    with file_path.open() as file:
        content = json.load(file)
    return _parse_content(content)


def _parse_content(
    content: Optional[Union[List[Any], Dict[Any, Any]]],
) -> FileContent:
    """Document content formatting."""
    mapping = {}
    if isinstance(content, dict):
        mapping = content
    if isinstance(content, list):
        mapping = {"values": content}
    for k in mapping:
        if not isinstance(k, str):
            msg = f"Expected all keys to be {str}: {mapping}"
            raise TypeError(msg)
    return mapping

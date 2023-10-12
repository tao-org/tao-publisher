"""File parsers utilities."""

import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml
from yaml.scanner import ScannerError

from .exceptions import FileContentError, FileExtensionInvalidError

FileContent = Dict[str, Any]
ParserFunc = Callable[[Path], FileContent]

_PARSERS: Dict[ParserFunc, List[str]] = {}


def get_valid_parsable_extensions() -> List[str]:
    """Get all extensions with existing parser."""
    extensions = set()
    for _extensions in _PARSERS.values():
        extensions.update(_extensions)
    return list(extensions)


def register_parser(*, extensions: List[str]) -> Callable[[ParserFunc], ParserFunc]:
    """Parser decorator."""

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


def parse_file(file_path: Path, /) -> FileContent:
    """Parse file.

    Raises:
        FileNotFoundError: file_path do not point to an existing file.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    if parser := get_parser(file_path.suffix):
        return parser(file_path)
    msg = f"Invalid file extension: {file_path}"
    raise FileExtensionInvalidError(msg)


def get_parser(file_ext: str, /) -> Optional[ParserFunc]:
    """Get parser for files with corresponding file extension."""
    for parser_func, extensions in _PARSERS.items():
        if file_ext in extensions:
            return parser_func
    return None


@register_parser(extensions=[".yaml", ".yml"])
def parse_yaml(file_path: Path, /) -> FileContent:
    """YAML document parser.

    Raises:
        FileNotFoundError: file_path do not point to an existing file.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    try:
        with file_path.open() as file:
            content = yaml.safe_load(file)
        return _parse_content(content)
    except ScannerError as err:
        msg = f"Invalid YAML file: {file_path}\n"
        msg += "Please check for syntax errors."
        raise FileContentError(msg) from err


@register_parser(extensions=[".json"])
def parse_json(file_path: Path, /) -> FileContent:
    """JSON document parser.

    Raises:
        FileNotFoundError: file_path do not point to an existing file.
        tao.utils.file.exceptions.FileExtensionInvalidError:
            file extension is not compatible.
        tao.utils.file.exceptions.FileContentError:
            file content could not be parsed.
    """
    try:
        with file_path.open() as file:
            content = json.load(file)
        return _parse_content(content)
    except json.JSONDecodeError as err:
        msg = f"Invalid JSON file: {file_path}\n"
        msg += "Please check for syntax errors."
        raise FileContentError(msg) from err


def _parse_content(
    content: Optional[Union[List[Any], Dict[Any, Any]]],
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

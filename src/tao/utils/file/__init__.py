"""File-related utilities package.

This package contains utilities for file management. This includes reading, writing
and other operations. The goal is _not_ to rewrite python standard libraries like
`os.path`, `pathlib`, or `shutil`.

Only features with added value will be implemented here.
"""

from typing import List

from .parser import get_parser, get_valid_parsable_extensions, parse_file
from .writer import get_valid_writable_extensions, get_writer, write_file


def get_valid_extensions() -> List[str]:
    """Get all extensions with existing parser and writer."""
    parsable_extensions = get_valid_parsable_extensions()
    writable_extensions = get_valid_writable_extensions()
    return list(set(parsable_extensions).intersection(writable_extensions))


__all__ = [
    "parse_file",
    "get_parser",
    "write_file",
    "get_writer",
    "get_valid_parsable_extensions",
    "get_valid_writable_extensions",
    "get_valid_extensions",
]

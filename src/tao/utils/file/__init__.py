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

"""File-related utilities package.

This package contains utilities for file management. This includes reading, writing
and other operations. The goal is _not_ to rewrite python standard libraries like
`os.path`, `pathlib`, or `shutil`.

Only features with added value will be implemented here.
"""

from .parser import get_parser, get_valid_parsable_extensions, parse_file
from .writer import get_valid_writable_extensions, get_writer, write_file


def get_valid_extensions() -> list[str]:
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

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

"""HTTP utilities.

Attributes:
    HTTP_401_UNAUTHORIZED(int): constant for HTTP 401 status code.
    HttpMethodName: type alias for HTTP methods names.
    SerializedFile:
        type alias for file serialized for upload. It is a tuple of:

        - file name (`str`)
        - file content (`bytes`)
        - file mime type (`str`)
"""

import mimetypes
import re
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

HTTP_401_UNAUTHORIZED = 401

HttpMethodName = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
SerializedFile = tuple[str, bytes, str]


def is_url(text: str, /) -> bool:
    """Return True if text is a valid URL, False otherwise.

    Examples:
        >>> is_url("test")
        False
        >>> is_url("test://test")
        False
        >>> is_url("https://www.csgroup.eu")
        True
    """
    parse_result = urlparse(text)
    return parse_result.scheme in ["http", "https"] and all(
        (parse_result.scheme, parse_result.netloc),
    )


def slugify(text: str, /) -> str:
    """Slugify string, URL-friendly and filename-friendly.

    Examples:
        >>> slugify("Hello World!")
        'hello-world'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def serialize_files(files: list[Path], /, *, ctx_path: Path) -> list[SerializedFile]:
    """Prepare files upload by transforming list of path to list of serialized files.

    Read each files and return list of `SerializedFile`. This method do not raise an
    error if a file is missing, files that do not exists will simply not be in the
    resulting list! You can check the length of the result against the length of the
    given files list to assert if no file was missed.

    Note:
        This method calls `serialize_file` for each file path,
        check it above to learn more!
    """
    files_data: list[SerializedFile] = []
    for file_path in files:
        file = serialize_file(file_path, ctx_path=ctx_path)
        if file:
            files_data.append(file)
    return files_data


def serialize_file(
    file_path: Path,
    /,
    *,
    ctx_path: Path,
) -> SerializedFile | None:
    """Prepare file upload by reading file and serializing it.

    Read file and return a SerializedFile that can be used with
    `requests` package "files" parameter. Mime type defaults to
    'text/plain', and if the file do not exists `None` is returned.
    """
    file_path = (ctx_path / file_path).resolve()
    if file_path.is_file():
        file_mimetype = mimetypes.guess_type(file_path)[0]
        if not file_mimetype:
            file_mimetype = "text/plain"
        with file_path.open("rb") as f:
            return (file_path.name, f.read(), file_mimetype)
    return None

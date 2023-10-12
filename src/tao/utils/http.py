"""HTTP utilities."""

import mimetypes
import re
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

HTTP_401_UNAUTHORIZED = 401

SerializedFile = Tuple[str, bytes, str]


def is_url(text: str, /) -> bool:
    """Return True if text is a valid URL, False otherwise.

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

    >>> slugify("Hello World!")
    'hello-world'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def serialize_files(files: List[Path], /, *, ctx_path: Path) -> List[SerializedFile]:
    """Prepare files upload by transforming list of path to list of file data."""
    files_data: List[SerializedFile] = []
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
) -> Optional[SerializedFile]:
    """Prepare file upload by reading path to file data."""
    file_path = (ctx_path / file_path).resolve()
    if file_path.is_file():
        file_mimetype = mimetypes.guess_type(file_path)[0]
        if not file_mimetype:
            file_mimetype = "text/plain"
        with file_path.open("rb") as f:
            return (file_path.name, f.read(), file_mimetype)
    return None

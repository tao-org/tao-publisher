"""HTTP utilities."""

import re
from urllib.parse import urlparse

HTTP_401_UNAUTHORIZED = 401


def is_uri(text: str) -> bool:
    """Return True if text is a valid URI, False otherwise."""
    parse_result = urlparse(text)
    return all([parse_result.scheme, parse_result.netloc])


def slugify(text: str) -> str:
    """Slugify string, URL-friendly and filename-friendly."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text

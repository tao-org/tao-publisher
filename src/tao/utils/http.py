"""HTTP utilities."""

from urllib.parse import urlparse

HTTP_401_UNAUTHORIZED = 401


def is_uri(text: str) -> bool:
    """Return True if text is a valid URI, False otherwise."""
    parse_result = urlparse(text)
    return all([parse_result.scheme, parse_result.netloc])

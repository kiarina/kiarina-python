from urllib.parse import urlparse


def is_uri(s: str) -> bool:
    return len(urlparse(s).scheme) > 1

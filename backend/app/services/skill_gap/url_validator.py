"""URL validation service for verifying LLM recommended learning resources."""

import re
from typing import Any, Dict, List

URL_REGEX = re.compile(
    r"^(?:http|https)://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

KNOWN_TRUSTED_DOMAINS = [
    "docs.python.org",
    "fastapi.tiangolo.com",
    "pytorch.org",
    "kubernetes.io",
    "docs.docker.com",
    "postgresql.org",
    "react.dev",
    "typescriptlang.org",
    "python.langchain.com",
    "coursera.org",
    "edx.org",
    "freecodecamp.org",
    "leetcode.com",
    "kaggle.com",
    "udemy.com",
    "github.com",
]


def validate_resource_url(url: str) -> bool:
    """Validates if a URL string follows standard HTTP/HTTPS format."""
    if not url or not isinstance(url, str):
        return False
    return bool(URL_REGEX.match(url.strip()))


def validate_and_flag_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Inspects resource URLs and adds 'flagged_for_review' status if invalid or untrusted."""
    validated = []
    for res in resources:
        item = dict(res)
        url = item.get("resource_url", "").strip()
        is_valid = validate_resource_url(url)
        is_trusted = any(domain in url.lower() for domain in KNOWN_TRUSTED_DOMAINS)

        item["is_valid_url"] = is_valid
        item["flagged_for_review"] = not (is_valid and is_trusted)
        validated.append(item)

    return validated

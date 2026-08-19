"""Security guardrails for prompt injection defense, input sanitization, and upload validation."""

import re
from typing import Tuple

from app.core.logging import logger

# Malicious prompt injection attack patterns
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+all\s+(previous\s+)?instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?previous\s+prompts", re.IGNORECASE),
    re.compile(r"override\s+(system\s+)?prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a\s+)?DAN", re.IGNORECASE),
    re.compile(r"jailbreak\s+mode", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
]

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


def sanitize_user_input_for_prompts(text: str) -> str:
    """Sanitizes user resume text or chat messages to prevent prompt injection attacks.

    Strips known jailbreak vectors and returns cleaned input.
    """
    if not text or not isinstance(text, str):
        return ""

    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(sanitized):
            logger.warning("Prompt injection pattern detected and stripped from user input.")
            sanitized = pattern.sub("[SANITIZED_SECURITY_VECTOR]", sanitized)

    return sanitized.strip()


def validate_resume_file_upload(
    filename: str, file_size: int, content_bytes: bytes
) -> Tuple[bool, str]:
    """Enforces strict extension checking, size limits, and virus scan stub validation."""
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension '{ext}'. Only .pdf and .docx files are permitted."

    if file_size > MAX_FILE_SIZE_BYTES or len(content_bytes) > MAX_FILE_SIZE_BYTES:
        return False, "File size exceeds maximum limit of 10MB."

    # Virus scan hook stub
    is_safe = stub_virus_scan_hook(content_bytes)
    if not is_safe:
        return False, "File failed security virus scanning."

    return True, "File validation passed."


def stub_virus_scan_hook(content_bytes: bytes) -> bool:
    """Stub hook for production ClamAV or AWS GuardDuty virus scanning."""
    # Check for EICAR test virus string
    if b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" in content_bytes:
        return False
    return True

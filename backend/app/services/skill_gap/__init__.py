"""Export module for skill gap services."""

from app.services.skill_gap.delta_calculator import compute_skill_delta
from app.services.skill_gap.url_validator import (
    validate_and_flag_resources,
    validate_resource_url,
)

__all__ = [
    "compute_skill_delta",
    "validate_resource_url",
    "validate_and_flag_resources",
]

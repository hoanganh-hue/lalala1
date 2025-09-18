"""
Utilities for MST (tax code) normalization and validation
"""
import re
from typing import Optional


def sanitize_mst(raw: str) -> str:
    """Keep digits only from the input string."""
    return re.sub(r"\D+", "", raw or "")


def normalize_mst(raw: str) -> Optional[str]:
    """Normalize MST to accepted format:
    - Accept 9 to 13 digits
    - If 9 digits, left-pad with one zero to 10 digits
    - Return None if invalid after sanitation
    """
    digits = sanitize_mst(raw)
    if not digits:
        return None
    if len(digits) < 9 or len(digits) > 13:
        return None
    if len(digits) == 9:
        digits = "0" + digits
    return digits


def is_valid_mst(raw: str) -> bool:
    """Check if raw MST is valid according to normalization rules."""
    return normalize_mst(raw) is not None



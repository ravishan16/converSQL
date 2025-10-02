"""Branding helpers for converSQL assets."""

from __future__ import annotations

import base64
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _PROJECT_ROOT / "assets"
_LOGO_PATH = _ASSETS_DIR / "conversql_logo.svg"
_FAVICON_PATH = _ASSETS_DIR / "favicon.png"


@lru_cache(maxsize=1)
def get_logo_svg() -> Optional[str]:
    """Return the SVG markup for the converSQL logo if available."""
    try:
        raw_svg = _LOGO_PATH.read_text(encoding="utf-8")

        # Remove XML declaration which prevents inline rendering in HTML contexts
        cleaned_svg = re.sub(r"^\s*<\?xml[^>]*\?>", "", raw_svg, count=1, flags=re.IGNORECASE | re.MULTILINE)

        return cleaned_svg.strip()
    except FileNotFoundError:
        return None


def get_logo_path() -> Path:
    """Return the filesystem path to the converSQL logo asset."""
    return _LOGO_PATH


@lru_cache(maxsize=1)
def get_logo_data_uri() -> Optional[str]:
    """Return a data URI suitable for embedding the SVG logo in HTML ``img`` tags."""
    svg = get_logo_svg()
    if not svg:
        return None

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


@lru_cache(maxsize=1)
def get_favicon_path() -> Optional[Path]:
    """Return the favicon path if it exists."""
    if _FAVICON_PATH.exists():
        return _FAVICON_PATH
    return None

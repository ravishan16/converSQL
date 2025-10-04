import base64
from pathlib import Path

from src.branding import get_favicon_path, get_logo_data_uri, get_logo_path, get_logo_svg


def test_get_logo_path_points_to_assets():
    path = get_logo_path()
    assert isinstance(path, Path)
    assert path.name == "conversql_logo.svg"
    assert path.parent.name == "assets"


def test_get_logo_svg_and_data_uri_consistency():
    svg = get_logo_svg()
    if svg is None:
        # Asset might be missing in some environments; function should handle gracefully
        assert get_logo_data_uri() is None
        return

    # If SVG exists, data URI should be a valid base64-encoded string
    data_uri = get_logo_data_uri()
    assert data_uri is not None
    assert data_uri.startswith("data:image/svg+xml;base64,")
    encoded = data_uri.split(",", 1)[1]
    # Ensure base64 decodes without error
    decoded = base64.b64decode(encoded)
    assert len(decoded) > 0


def test_get_favicon_path_optional():
    fav = get_favicon_path()
    if fav is not None:
        assert fav.exists()
"""
Smoke test for app initialization.

This test ensures that the application can be imported and core initialization
paths work without network calls or full UI rendering.
"""

import sys
from unittest.mock import MagicMock, patch


def test_app_imports_successfully():
    """Test that the app.py module can be imported without errors."""
    # Mock streamlit to prevent UI operations
    sys.modules["streamlit"] = MagicMock()

    try:
        import app  # noqa: F401

        assert True, "app.py imported successfully"
    except ImportError as e:
        assert False, f"Failed to import app.py: {e}"


def test_app_logic_imports_successfully():
    """Test that src.app_logic can be imported."""
    try:
        from src import app_logic  # noqa: F401

        assert True, "src.app_logic imported successfully"
    except ImportError as e:
        assert False, f"Failed to import src.app_logic: {e}"


def test_app_logic_initialize_without_streamlit():
    """Test that initialize_app_data can be called with mocked streamlit."""

    # Create a session state mock that supports both dict and attribute access
    class SessionStateMock:
        def __init__(self):
            self._data = {}

        def __contains__(self, key):
            return key in self._data

        def __setitem__(self, key, value):
            self._data[key] = value

        def __getitem__(self, key):
            return self._data[key]

        def __setattr__(self, key, value):
            if key == "_data":
                super().__setattr__(key, value)
            else:
                self._data[key] = value

        def __getattr__(self, key):
            if key == "_data":
                return super().__getattribute__(key)
            return self._data.get(key)

        def setdefault(self, key, value):
            return self._data.setdefault(key, value)

    # Mock streamlit with custom session state
    mock_session_state = SessionStateMock()
    mock_st = MagicMock()
    mock_st.session_state = mock_session_state

    # Mock spinner context manager
    mock_spinner = MagicMock()
    mock_spinner.__enter__ = MagicMock(return_value=None)
    mock_spinner.__exit__ = MagicMock(return_value=None)
    mock_st.spinner.return_value = mock_spinner

    # Mock the data services to avoid file I/O
    with patch("src.app_logic.st", mock_st):
        with patch("src.app_logic.load_parquet_files", return_value=[]):
            with patch("src.app_logic.load_schema_context", return_value=""):
                with patch("src.app_logic.load_ai_service", return_value=MagicMock(is_available=lambda: False)):
                    from src.app_logic import initialize_app_data

                    # Should not raise any exceptions
                    initialize_app_data()

                    # Verify session state was initialized
                    assert "generated_sql" in mock_session_state
                    assert "ai_error" in mock_session_state
                    assert "show_edit_sql" in mock_session_state
                    assert "_rendered_this_run" in mock_session_state


def test_core_imports_successfully():
    """Test that src.core module can be imported."""
    try:
        from src import core  # noqa: F401

        assert True, "src.core imported successfully"
    except ImportError as e:
        assert False, f"Failed to import src.core: {e}"


def test_ai_service_imports_successfully():
    """Test that src.ai_service module can be imported."""
    try:
        from src import ai_service  # noqa: F401

        assert True, "src.ai_service imported successfully"
    except ImportError as e:
        assert False, f"Failed to import src.ai_service: {e}"

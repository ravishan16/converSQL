import pandas as pd
import pytest
import streamlit as st

from src.visualization import (
    _get_column_types,
    _init_chart_state,
    _validate_chart_params,
    get_chart_recommendation,
    make_chart,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": ["X", "Y", "Z"],
            "D": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
            "E": ["red", "blue", "green"],
        }
    )


@pytest.fixture
def mixed_type_df():
    """DataFrame with mixed types for testing sort behavior"""
    return pd.DataFrame(
        {"id": [1, 2, 3], "mixed": ["10", 20, "30"], "category": ["a", "b", "c"]}  # Mixed strings and numbers
    )


def test_make_chart_basic(sample_df):
    """Test basic chart creation for each type"""
    chart = make_chart(sample_df, "Bar", "C", "A")
    assert chart is not None
    assert chart.mark == "bar"

    chart = make_chart(sample_df, "Line", "D", "A")
    assert chart is not None
    assert chart.mark == "line"

    chart = make_chart(sample_df, "Scatter", "A", "B")
    assert chart is not None
    assert chart.mark == "circle"

    chart = make_chart(sample_df, "Histogram", "A", None)
    assert chart is not None
    assert chart.mark == "bar"

    chart = make_chart(sample_df, "Heatmap", "A", "B")
    assert chart is not None
    assert chart.mark == "rect"


def test_make_chart_color(sample_df):
    """Test color encoding in charts"""
    # Test categorical color
    chart = make_chart(sample_df, "Bar", "C", "A", color="E")
    assert chart is not None
    assert chart.encoding.color is not None
    assert chart.encoding.color.shorthand == "E"

    # Test numeric color
    chart = make_chart(sample_df, "Scatter", "A", "B", color="B")
    assert chart is not None
    assert chart.encoding.color is not None
    assert chart.encoding.color.shorthand == "B"  # Test invalid color
    chart = make_chart(sample_df, "Bar", "C", "A", color="Missing")
    assert chart is None


def test_make_chart_validation(sample_df, mixed_type_df):
    """Test input validation in make_chart"""
    # Invalid chart type
    chart = make_chart(sample_df, "Invalid", "A", "B")
    assert chart is None

    # Missing required column
    chart = make_chart(sample_df, "Bar", "Missing", "A")
    assert chart is None

    # Empty DataFrame
    chart = make_chart(pd.DataFrame(), "Bar", "A", "B")
    assert chart is None

    # None DataFrame
    chart = make_chart(None, "Bar", "A", "B")
    assert chart is None

    # Test basic sort
    chart = make_chart(sample_df, "Bar", "C", "A", sort_by="A")
    assert chart is not None

    # Test mixed type sorting (should coerce to string)
    chart = make_chart(mixed_type_df, "Bar", "category", "mixed")
    assert chart is not None

    chart = make_chart(sample_df, "Bar", "C", "A", color="Missing")
    assert chart is None


def test_validate_chart_params(sample_df):
    """Test the chart parameter validation"""
    # Valid parameters
    valid, error = _validate_chart_params({"chart": "Bar", "x": "C", "y": "A"}, list(sample_df.columns), sample_df)
    assert valid
    assert error is None

    # Invalid chart type
    valid, error = _validate_chart_params({"chart": "Invalid", "x": "C", "y": "A"}, list(sample_df.columns), sample_df)
    assert not valid
    assert "Invalid chart type" in error

    # Missing required column
    valid, error = _validate_chart_params(
        {"chart": "Bar", "x": "Missing", "y": "A"}, list(sample_df.columns), sample_df
    )
    assert not valid
    assert "Invalid x-axis" in error

    # Invalid histogram column type
    valid, error = _validate_chart_params(
        {"chart": "Histogram", "x": "C", "y": None}, list(sample_df.columns), sample_df
    )
    assert not valid
    assert "Histogram requires numeric" in error


def test_get_chart_recommendation():
    """Test chart type recommendations"""
    # Time series: 1 numeric + 1 datetime
    df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=3), "value": [1, 2, 3]})
    chart_type, x, y = get_chart_recommendation(df)
    assert chart_type == "Line"
    assert x == "date"
    assert y == "value"

    # Categorical + numeric
    df = pd.DataFrame({"category": ["A", "B", "C"], "value": [1, 2, 3]})
    chart_type, x, y = get_chart_recommendation(df)
    assert chart_type == "Bar"
    assert x == "category"
    assert y == "value"

    # Multiple numerics
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})
    chart_type, x, y = get_chart_recommendation(df)
    assert chart_type == "Heatmap"
    assert x == "x"
    assert y == "y"

    # No clear recommendation
    df = pd.DataFrame({"a": ["X", "Y", "Z"], "b": ["1", "2", "3"]})
    chart_type, x, y = get_chart_recommendation(df)
    assert chart_type is None
    assert x is None
    assert y is None


def test_column_type_caching(sample_df):
    """Test that column type detection is cached"""
    # First call should cache
    numeric1, datetime1, categorical1 = _get_column_types(sample_df)

    # Second call should use cache
    numeric2, datetime2, categorical2 = _get_column_types(sample_df)

    assert numeric1 == numeric2
    assert datetime1 == datetime2
    assert categorical1 == categorical2


def test_init_chart_state(sample_df, monkeypatch):
    """Test chart state initialization"""
    # Mock session state
    with monkeypatch.context() as m:
        # Empty session state
        m.setattr(st, "session_state", {})

        keys, cols = _init_chart_state(sample_df, "test")

        # Check key structure
        assert set(keys.keys()) == {"chart", "x", "y", "color"}
        assert all(k.startswith("test_") for k in keys.values())

        # Check column list
        assert cols == list(sample_df.columns)

        # Verify session state was initialized
        assert st.session_state.get(keys["chart"]) is not None
        assert st.session_state.get(keys["x"]) is not None
        assert st.session_state.get(keys["y"]) is not None

        # Try with AI recommendations
        m.setattr(st, "session_state", {"ai_chart_type": "Bar", "ai_chart_x": "C", "ai_chart_y": "A"})

        keys, cols = _init_chart_state(sample_df, "test2")
        assert st.session_state.get(keys["chart"]) == "Bar"
        assert st.session_state.get(keys["x"]) == "C"
        assert st.session_state.get(keys["y"]) == "A"
        assert st.session_state.get(keys["y"]) == "A"

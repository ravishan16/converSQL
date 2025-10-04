import pandas as pd
import pytest

from src.visualization import get_chart_recommendation, make_chart


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": ["X", "Y", "Z"],
            "D": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        }
    )


def test_make_chart(sample_df):
    chart = make_chart(sample_df, "Bar", "C", "A")
    assert chart is not None
    assert chart.mark == "bar"

    chart = make_chart(sample_df, "Line", "D", "A")
    assert chart is not None
    assert chart.mark == "line"

    chart = make_chart(sample_df, "Scatter", "A", "B")
    assert chart is not None
    assert chart.mark == "circle"

    chart = make_chart(sample_df, "Histogram", "A", "count()")
    assert chart is not None
    assert chart.mark == "bar"

    chart = make_chart(sample_df, "Heatmap", "A", "B")
    assert chart is not None
    assert chart.mark == "rect"

    chart = make_chart(sample_df, "Invalid", "A", "B")
    assert chart is None


def test_get_chart_recommendation():
    # Test case 1: 1 numeric, 1 categorical
    df1 = pd.DataFrame({"A": [1, 2, 3], "B": ["X", "Y", "Z"]})
    chart_type, x, y = get_chart_recommendation(df1)
    assert chart_type == "Bar"
    assert x == "B"
    assert y == "A"

    # Test case 2: 1 numeric, 1 datetime
    df2 = pd.DataFrame({"A": [1, 2, 3], "B": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])})
    chart_type, x, y = get_chart_recommendation(df2)
    assert chart_type == "Line"
    assert x == "B"
    assert y == "A"

    # Test case 3: 2 numeric
    df3 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    chart_type, x, y = get_chart_recommendation(df3)
    assert chart_type == "Scatter"
    assert x == "A"
    assert y == "B"

    # Test case 4: >2 numeric, 0 categorical
    df4 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
    chart_type, x, y = get_chart_recommendation(df4)
    assert chart_type == "Heatmap"
    assert x == "A"
    assert y == "B"

    # Test case 5: 1 categorical, >1 numeric
    df5 = pd.DataFrame({"A": ["X", "Y", "Z"], "B": [1, 2, 3], "C": [4, 5, 6]})
    chart_type, x, y = get_chart_recommendation(df5)
    assert chart_type == "Bar"
    assert x == "A"
    assert y == "B"

    # Test case 6: No recommendation
    df6 = pd.DataFrame({"A": ["X", "Y", "Z"], "B": ["a", "b", "c"]})
    chart_type, x, y = get_chart_recommendation(df6)
    assert chart_type is None
    assert x is None
    assert y is None

"""Tests for visualization dataframe fallback precedence and chart state initialization.

Focus areas:
 1. _resolve_dataframe precedence: explicit > manual > ai
 2. _init_chart_state uses AI recommendations when valid, else sensible defaults.
"""

import pandas as pd
import streamlit as st

from src.visualization import _init_chart_state, _resolve_dataframe, render_visualization


def _reset_session_state():
    # Clear all existing state keys to avoid cross-test interference
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def test_resolve_dataframe_explicit_wins():
    _reset_session_state()
    manual_df = pd.DataFrame({"a": [1, 2]})
    ai_df = pd.DataFrame({"b": [3, 4]})
    explicit_df = pd.DataFrame({"c": [5, 6]})
    st.session_state["manual_query_result_df"] = manual_df
    st.session_state["ai_query_result_df"] = ai_df

    resolved = _resolve_dataframe(explicit_df)
    assert resolved is explicit_df


def test_resolve_dataframe_manual_when_no_explicit():
    _reset_session_state()
    manual_df = pd.DataFrame({"a": [1, 2]})
    ai_df = pd.DataFrame({"b": [3, 4]})
    st.session_state["manual_query_result_df"] = manual_df
    st.session_state["ai_query_result_df"] = ai_df

    resolved = _resolve_dataframe(None)
    assert resolved is manual_df


def test_resolve_dataframe_ai_when_no_manual():
    _reset_session_state()
    ai_df = pd.DataFrame({"b": [3, 4]})
    st.session_state["ai_query_result_df"] = ai_df

    resolved = _resolve_dataframe(None)
    assert resolved is ai_df


def test_init_chart_state_uses_ai_recommendations():
    _reset_session_state()
    df = pd.DataFrame({"cat": ["x", "y"], "val": [10, 20], "val2": [1, 2]})
    # AI recommendations
    st.session_state["ai_chart_type"] = "Bar"
    st.session_state["ai_chart_x"] = "cat"
    st.session_state["ai_chart_y"] = "val"
    st.session_state["ai_chart_color"] = "val2"

    keys, cols = _init_chart_state(df, "test")

    assert st.session_state[keys["chart"]] == "Bar"
    assert st.session_state[keys["x"]] == "cat"
    assert st.session_state[keys["y"]] == "val"
    assert st.session_state[keys["color"]] == "val2"


def test_init_chart_state_histogram_sets_y_none():
    _reset_session_state()
    df = pd.DataFrame({"metric": [1, 2, 3, 4]})
    st.session_state["ai_chart_type"] = "Histogram"
    st.session_state["ai_chart_x"] = "metric"
    st.session_state["ai_chart_y"] = "SHOULD_IGNORE"  # Should be ignored for histogram
    st.session_state["ai_chart_color"] = None

    keys, _ = _init_chart_state(df, "hist")
    assert st.session_state[keys["chart"]] == "Histogram"
    assert st.session_state[keys["x"]] == "metric"
    assert st.session_state[keys["y"]] is None


def test_render_visualization_clamps_invalid_session_state(tmp_path):
    # Regression for ValueError: None is not in list when selectbox index had None/invalid
    _reset_session_state()
    df = pd.DataFrame({"cat": ["a", "b"], "val": [1, 2]})
    # Seed obviously invalid selections
    st.session_state["chart_viz"] = "Bar"
    st.session_state["x_viz"] = None
    st.session_state["y_viz"] = "does_not_exist"
    st.session_state["color_viz"] = "also_missing"

    # Just verify it does not raise; we don't assert on Streamlit UI
    try:
        render_visualization(df, container_key="viz")
    except Exception as e:
        raise AssertionError(f"render_visualization should not raise, but got: {e}")

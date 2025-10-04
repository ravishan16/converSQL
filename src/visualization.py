"""Visualization helpers for the converSQL Streamlit UI."""

from typing import Literal, cast

import altair as alt
import pandas as pd
import streamlit as st

# Allow rendering large datasets without silently dropping charts
try:
    alt.data_transformers.disable_max_rows()
except Exception:
    pass

ALLOWED_CHART_TYPES = ["Bar", "Line", "Scatter", "Histogram", "Heatmap"]


def _resolve_dataframe(explicit_df: pd.DataFrame | None) -> pd.DataFrame:
    """Resolve which DataFrame to visualize based on precedence.

    Order: explicit_df > st.session_state["manual_query_result_df"] > st.session_state["ai_query_result_df"].
    Returns an empty DataFrame if none found.
    """
    if explicit_df is not None:
        return explicit_df

    manual_df = st.session_state.get("manual_query_result_df")
    if isinstance(manual_df, pd.DataFrame):
        return manual_df

    ai_df = st.session_state.get("ai_query_result_df")
    if isinstance(ai_df, pd.DataFrame):
        return ai_df

    return pd.DataFrame()


def _init_chart_state(df: pd.DataFrame, container_key: str):
    """Initialize chart control state using AI recommendations when valid.
    Uses cached column types for performance. Returns (keys, columns) tuple.
    """
    prefix = f"{container_key}_"  # Ensure consistent prefix for all keys
    keys = {
        "chart": f"{prefix}chart",
        "x": f"{prefix}x",
        "y": f"{prefix}y",
        "color": f"{prefix}color",
    }

    cols = list(df.columns)
    if not cols:
        return keys, cols

    # Get cached column types
    numeric_cols, datetime_cols, categorical_cols = _get_column_types(df)

    # Validate existing column references
    def _valid(col: str | None) -> bool:
        return col is None or (isinstance(col, str) and col in cols)

    # Try AI recommendations, then fallback to smart defaults
    ai_chart = st.session_state.get("ai_chart_type")
    ai_x = st.session_state.get("ai_chart_x") if _valid(st.session_state.get("ai_chart_x")) else None
    ai_y = st.session_state.get("ai_chart_y") if _valid(st.session_state.get("ai_chart_y")) else None
    ai_color = st.session_state.get("ai_chart_color") if _valid(st.session_state.get("ai_chart_color")) else None

    # Validate chart type and get recommendations if needed
    chart_type = ai_chart if ai_chart in ALLOWED_CHART_TYPES else None
    if not chart_type:
        chart_type, rec_x, rec_y = get_chart_recommendation(df)
        # If recommendation fails, build safe default
        if not chart_type:
            if numeric_cols and categorical_cols:
                chart_type = "Bar"
                rec_x, rec_y = categorical_cols[0], numeric_cols[0]
            elif len(numeric_cols) >= 2:
                chart_type = "Scatter"
                rec_x, rec_y = numeric_cols[0], numeric_cols[1]
            elif numeric_cols:
                chart_type = "Histogram"
                rec_x, rec_y = numeric_cols[0], None
            else:
                # Last resort: bar chart with first two columns
                chart_type = "Bar"
                rec_x, rec_y = cols[0], cols[1] if len(cols) > 1 else cols[0]

        # Use recommendations if AI values not valid
        x_axis = ai_x if ai_x else rec_x
        y_axis = ai_y if ai_y else rec_y
    else:
        # Using AI chart type - ensure x/y are valid
        x_axis = ai_x if ai_x else cols[0]
        y_axis = ai_y if chart_type != "Histogram" else None

    # Special handling for Histogram
    if chart_type == "Histogram":
        if x_axis not in numeric_cols:
            x_axis = numeric_cols[0] if numeric_cols else cols[0]
        y_axis = None  # Always None for Histogram

    # Initialize session state (only if not already set)
    if keys["chart"] not in st.session_state:
        st.session_state[keys["chart"]] = chart_type
    if keys["x"] not in st.session_state:
        st.session_state[keys["x"]] = x_axis
    if keys["y"] not in st.session_state:
        st.session_state[keys["y"]] = y_axis
    if keys["color"] not in st.session_state:
        st.session_state[keys["color"]] = ai_color

    return keys, cols


def _safe_index(options: list, value, default: int = 0) -> int:
    """Return a safe index into options for Streamlit selectbox.

    - If options is empty, return 0
    - If value is None or not present, return default (bounded to options)
    """
    if not options:
        return 0
    try:
        return options.index(value) if value in options else min(max(default, 0), len(options) - 1)
    except Exception:
        return min(max(default, 0), len(options) - 1)


def make_chart(
    df: pd.DataFrame,
    chart_type: str,
    x: str,
    y: str | None,
    color: str | None = None,
    sort_by: str | None = None,
    sort_dir: str = "Ascending",
) -> alt.Chart | None:
    """
    Create an Altair chart based on the given parameters.
    Includes input validation and error handling.

    Returns:
        alt.Chart | None: The configured chart or None if invalid parameters
    """
    # Input validation
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.error("No data available for visualization")
        return None

    if not isinstance(x, str) or x not in df.columns:
        st.error(f"Invalid x-axis column: {x}")
        return None

    if y is not None and (not isinstance(y, str) or y not in df.columns):
        st.error(f"Invalid y-axis column: {y}")
        return None

    if color is not None and color not in df.columns:
        st.error(f"Invalid color column: {color}")
        return None

    if chart_type not in ALLOWED_CHART_TYPES:
        st.error(f"Unsupported chart type: {chart_type}")
        return None

    # Verify numeric columns for Histogram
    if chart_type == "Histogram":
        numeric_cols = list(df.select_dtypes(include=["number"]).columns)
        if x not in numeric_cols:
            st.error(f"Histogram requires numeric x-axis. Column '{x}' is {df[x].dtype}")
            return None

    # Configure axis sort
    sort_arg_x = None
    if chart_type in {"Bar", "Heatmap", "Scatter", "Line"} and sort_by:
        try:
            # Validate sort column exists
            if sort_by not in df.columns:
                st.warning(f"Invalid sort column '{sort_by}'. Sorting disabled.")
            else:
                order = "descending" if sort_dir == "Descending" else "ascending"
                # Always use SortField for consistent behavior
                sort_arg_x = alt.SortField(field=sort_by, order=cast(Literal["ascending", "descending"], order))
        except Exception as e:
            st.warning(f"Sort configuration failed: {str(e)}")
            sort_arg_x = None

    try:
        # Create base chart with appropriate mark and encoding
        base = alt.Chart(df)

        if chart_type == "Bar":
            chart = base.mark_bar().encode(x=alt.X(x, sort=sort_arg_x), y=y)
        elif chart_type == "Line":
            chart = base.mark_line().encode(x=x, y=y)
        elif chart_type == "Scatter":
            chart = base.mark_circle().encode(x=x, y=y)
        elif chart_type == "Histogram":
            chart = base.mark_bar().encode(x=alt.X(x, bin=True), y="count()")
        elif chart_type == "Heatmap":
            chart = base.mark_rect().encode(x=alt.X(x, sort=sort_arg_x), y=y)
        else:
            st.error(f"Unhandled chart type: {chart_type}")
            return None

        # Add color encoding if specified
        if color:
            try:
                chart = chart.encode(color=alt.Color(shorthand=color))
            except Exception as e:
                st.warning(f"Color encoding failed: {str(e)}")

        return chart.properties(width="container")

    except Exception as e:
        st.error(f"Chart creation failed: {str(e)}")
        return None


@st.cache_data(show_spinner=False)
def _get_column_types(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    """Cache column type classification to avoid redundant dtype checks."""
    numeric = list(df.select_dtypes(include=["number"]).columns)
    datetime = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)
    categorical = list(df.select_dtypes(exclude=["number", "datetime"]).columns)
    return numeric, datetime, categorical


def get_chart_recommendation(df: pd.DataFrame) -> tuple[str | None, str | None, str | None]:
    """
    Recommend a chart type and axes based on the DataFrame schema.
    Uses cached column type checks for performance.
    """
    # Get cached column types
    numeric_cols, datetime_cols, categorical_cols = _get_column_types(df)

    # Order recommendations by specificity and common use cases
    if len(numeric_cols) == 1 and len(datetime_cols) == 1:
        return "Line", datetime_cols[0], numeric_cols[0]  # Time series first
    elif len(categorical_cols) == 1 and len(numeric_cols) >= 1:
        return "Bar", categorical_cols[0], numeric_cols[0]  # Bar charts for categories
    elif len(numeric_cols) == 2:
        return "Scatter", numeric_cols[0], numeric_cols[1]  # Scatter for numeric pairs
    elif len(numeric_cols) > 2 and not categorical_cols:
        return "Heatmap", numeric_cols[0], numeric_cols[1]  # Heatmap for multiple numerics

    return None, None, None


def _validate_chart_params(params: dict, cols: list[str], df: pd.DataFrame) -> tuple[bool, str | None]:
    """Validate chart parameters and return (is_valid, error_message)."""
    if not params.get("chart"):
        return False, "No chart type specified"
    if params["chart"] not in ALLOWED_CHART_TYPES:
        return False, f"Invalid chart type: {params['chart']}"
    if not params.get("x") or params["x"] not in cols:
        return False, f"Invalid x-axis column: {params.get('x')}"
    if params["chart"] != "Histogram":
        if not params.get("y") or params["y"] not in cols:
            return False, f"Invalid y-axis column: {params.get('y')}"
    if params.get("color") and params["color"] not in cols:
        return False, f"Invalid color column: {params.get('color')}"
    if params["chart"] == "Histogram":
        num_cols = list(df.select_dtypes(include=["number"]).columns)
        if params["x"] not in num_cols:
            return False, f"Histogram requires numeric x-axis, got {df[params['x']].dtype}"
    return True, None


def _build_and_render(df: pd.DataFrame, params: dict, keys: dict) -> bool:
    """Build and render chart with error handling and automatic type coercion."""
    try:
        # Work on a copy for sorting and get columns
        plot_df = df.copy()
        available_cols = list(plot_df.columns)

        # Handle sorting with type coercion
        sort_col = params.get("sort_col")
        if sort_col and sort_col in plot_df.columns:
            ascending = params.get("sort_dir", "Ascending") == "Ascending"
            try:
                plot_df = plot_df.sort_values(by=sort_col, ascending=ascending)
            except Exception as e:
                st.warning(f"Sort failed, converting to string: {str(e)}")
                plot_df[sort_col] = plot_df[sort_col].astype(str)
                plot_df = plot_df.sort_values(by=sort_col, ascending=ascending)

        # Special handling for histogram
        y_arg = params.get("y")
        if params.get("chart") == "Histogram":
            numeric_cols = list(plot_df.select_dtypes(include=["number"]).columns)
            if params.get("x") not in numeric_cols:
                if numeric_cols:
                    # Handle histogram column type coercion
                    params["x"] = numeric_cols[0]
                    st.session_state[keys["x"]] = numeric_cols[0]
                    y_arg = None  # Histogram doesn't use y-axis
                else:
                    # Fall back to bar chart if no numeric columns
                    st.warning("No numeric columns available for histogram")
                    params["chart"] = "Bar"
                    y_arg = params.get("y") or available_cols[0]  # Ensure y-axis for bar chart

        chart = make_chart(
            plot_df,
            params.get("chart", "Bar"),
            params.get("x") or available_cols[0],
            None if params.get("chart") == "Histogram" else y_arg,
            params.get("color"),
            params.get("sort_col"),
            params.get("sort_dir", "Ascending"),
        )

        if chart:
            st.altair_chart(chart, use_container_width=True)
            return True
        return False

    except Exception as e:
        st.error(f"Chart generation failed: {str(e)}")
        return False


def render_visualization(df: pd.DataFrame, container_key: str = "viz"):
    """Render the visualization layer with improved error handling and validation.

    Does not mutate the provided DataFrame when applying sorting.
    """
    st.markdown(
        """
        <div class='section-card__header'>
            <h3>📊 Data Visualization</h3>
            <p>Explore your query results through interactive charts</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Input validation with helpful messages
    if df is None:
        st.error("No data provided for visualization")
        return
    if df.empty:
        st.info("Dataset is empty - nothing to visualize")
        return
    if not isinstance(df, pd.DataFrame):
        st.error(f"Expected pandas DataFrame, got {type(df)}")
        return

    # Initialize state and get column info
    keys, cols = _init_chart_state(df, container_key)
    if not cols:
        st.error("No columns available in the dataset")
        return

    # Track state keys
    sort_col_key = f"sort_col_{container_key}"
    sort_dir_key = f"sort_dir_{container_key}"
    last_valid_key = f"last_valid_params_{container_key}"

    # Read current selections with validation
    chart_type = st.session_state.get(keys["chart"], "Bar")
    x_col = st.session_state.get(keys["x"], cols[0])
    y_col = None if chart_type == "Histogram" else st.session_state.get(keys["y"])
    color_col = st.session_state.get(keys["color"]) if st.session_state.get(keys["color"]) in cols else None

    # Ensure sort state is valid
    default_sort = y_col if y_col in cols else None
    sort_col = st.session_state.get(sort_col_key)
    if sort_col not in cols:
        sort_col = default_sort
        st.session_state[sort_col_key] = sort_col
    if sort_dir_key not in st.session_state:
        st.session_state[sort_dir_key] = "Ascending"

    # Render control UI with smart layout
    st.markdown("<div class='control-group'>", unsafe_allow_html=True)
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        st.selectbox(
            "Chart type",
            ALLOWED_CHART_TYPES,
            index=_safe_index(ALLOWED_CHART_TYPES, chart_type),
            key=keys["chart"],
            help="Choose visualization type",
        )
    with ctrl_col2:
        st.selectbox("X-axis", cols, index=_safe_index(cols, x_col), key=keys["x"], help="Select X-axis column")
    st.markdown("</div>", unsafe_allow_html=True)

    # Handle Y-axis and color in compact layout
    st.markdown("<div class='control-group chart-controls'>", unsafe_allow_html=True)
    y_color_cols = st.columns(2)
    if chart_type == "Histogram":
        with y_color_cols[0]:
            st.markdown(
                """
                <div class='disabled-control'>
                    <label>Y-axis</label>
                    <div class='info-text'>Not required for Histogram (uses count)</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        with y_color_cols[0]:
            st.selectbox("Y-axis", cols, index=_safe_index(cols, y_col), key=keys["y"], help="Select Y-axis column")
    st.markdown("</div>", unsafe_allow_html=True)

    # Color selector with None option
    color_options = [None] + list(cols)
    with y_color_cols[1]:
        st.selectbox(
            "Color / Group by",
            color_options,
            index=_safe_index(color_options, color_col),
            key=keys["color"],
            help="Optional grouping column",
            format_func=lambda x: "— None —" if x is None else str(x),
        )

    # Sort controls
    st.markdown("<div class='control-group'>", unsafe_allow_html=True)
    sort_by_options = [None] + list(cols)
    sort_cols = st.columns(2)
    with sort_cols[0]:
        st.selectbox(
            "Sort by",
            sort_by_options,
            index=_safe_index(sort_by_options, sort_col),
            key=sort_col_key,
            help="Sort data before plotting",
            format_func=lambda x: "— None —" if x is None else str(x),
        )
    with sort_cols[1]:
        st.selectbox("Sort direction", ["Ascending", "Descending"], key=sort_dir_key)
    st.markdown("</div>", unsafe_allow_html=True)

    # Build current parameter set
    current_params = {
        "chart": st.session_state.get(keys["chart"], "Bar"),
        "x": st.session_state.get(keys["x"]),
        "y": st.session_state.get(keys["y"]),
        "color": st.session_state.get(keys["color"]),
        "sort_col": st.session_state.get(sort_col_key),
        "sort_dir": st.session_state.get(sort_dir_key, "Ascending"),
    }

    # Validate and render
    valid, error = _validate_chart_params(current_params, cols, df)
    if valid:
        if _build_and_render(df, current_params, keys):
            st.session_state[last_valid_key] = current_params
        else:
            # Try fallback to last valid state
            fallback = st.session_state.get(last_valid_key)
            if fallback and _build_and_render(df, fallback, keys):
                st.info("Using last valid chart configuration")
            else:
                # Final fallback: get fresh recommendation
                rec_chart, rec_x, rec_y = get_chart_recommendation(df)
                safe_params = {
                    "chart": rec_chart or "Bar",
                    "x": rec_x or cols[0],
                    "y": rec_y if rec_chart != "Histogram" else None,
                    "color": None,
                    "sort_col": None,
                    "sort_dir": "Ascending",
                }
                if _build_and_render(df, safe_params, keys):
                    st.session_state[last_valid_key] = safe_params
                    st.info("Using recommended chart configuration")
                else:
                    st.error("Unable to generate any valid chart")
                    st.dataframe(df)  # Show raw data as last resort
    else:
        st.warning(error)
        # Show last valid state if available
        fallback = st.session_state.get(last_valid_key)
        if fallback and _build_and_render(df, fallback, keys):
            st.info("Showing previous valid configuration while fixing errors")


import streamlit as st
import pandas as pd
import altair as alt

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

    Returns a tuple: (keys, columns), where keys is a dict with keys for chart/x/y/color.
    """
    keys = {
        "chart": f"chart_{container_key}",
        "x": f"x_{container_key}",
        "y": f"y_{container_key}",
        "color": f"color_{container_key}",
    }

    cols = list(df.columns)

    # AI recommendations from session
    ai_chart = st.session_state.get("ai_chart_type")
    ai_x = st.session_state.get("ai_chart_x")
    ai_y = st.session_state.get("ai_chart_y")
    ai_color = st.session_state.get("ai_chart_color")

    # Validate AI hints
    def _valid(col: str | None) -> bool:
        return col is None or (isinstance(col, str) and col in cols)

    # Use recommendation if valid; otherwise compute from data
    rec_chart, rec_x, rec_y = get_chart_recommendation(df)

    chart_type = ai_chart if ai_chart in {"Bar", "Line", "Scatter", "Histogram", "Heatmap"} else rec_chart
    x_axis = ai_x if _valid(ai_x) else rec_x
    y_axis = ai_y if _valid(ai_y) else rec_y
    color = ai_color if _valid(ai_color) else None

    # Histogram: y should be None (count aggregation)
    if chart_type == "Histogram":
        y_axis = None

    # Fallbacks if still missing
    if chart_type is None:
        # Prefer Bar if we have at least 1 categorical + 1 numeric
        num_cols = list(df.select_dtypes(include=["number"]).columns)
        cat_cols = [c for c in cols if c not in num_cols]
        if cat_cols and num_cols:
            chart_type = "Bar"
            x_axis = x_axis or cat_cols[0]
            y_axis = y_axis or num_cols[0]
        elif len(num_cols) >= 2:
            chart_type = "Scatter"
            x_axis = x_axis or num_cols[0]
            y_axis = y_axis or num_cols[1]
        elif num_cols:
            chart_type = "Histogram"
            x_axis = x_axis or num_cols[0]
            y_axis = None

    # Seed session state
    if keys["chart"] not in st.session_state:
        st.session_state[keys["chart"]] = chart_type
    if keys["x"] not in st.session_state:
        st.session_state[keys["x"]] = x_axis
    if keys["y"] not in st.session_state:
        st.session_state[keys["y"]] = y_axis
    if keys["color"] not in st.session_state:
        st.session_state[keys["color"]] = color

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
):
    """
    Create an Altair chart based on the given parameters.
    """
    # Configure axis sort for categorical X where appropriate
    sort_arg_x = None
    if chart_type in {"Bar", "Heatmap", "Scatter", "Line"} and sort_by:
        order = "descending" if sort_dir == "Descending" else "ascending"
        if y is not None and sort_by == y and chart_type == "Bar":
            # Convenient shorthand: sort bars by Y
            sort_arg_x = "-y" if order == "descending" else "y"
        else:
            try:
                import altair as _alt
                sort_arg_x = _alt.SortField(field=sort_by, order=order)
            except Exception:
                sort_arg_x = None

    if chart_type == "Bar":
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(x, sort=sort_arg_x),
            y=y,
        )
    elif chart_type == "Line":
        chart = alt.Chart(df).mark_line().encode(
            x=x,
            y=y,
        )
    elif chart_type == "Scatter":
        chart = alt.Chart(df).mark_circle().encode(
            x=x,
            y=y,
        )
    elif chart_type == "Histogram":
        # For histogram, Altair expects a quantitative column on X
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(x, bin=True),
            y='count()',
        )
    elif chart_type == "Heatmap":
        chart = alt.Chart(df).mark_rect().encode(
            x=alt.X(x, sort=sort_arg_x),
            y=y,
        )
    else:
        st.error("Invalid chart type")
        return None

    if color:
        chart = chart.encode(color=color)

    return chart.properties(width="container")

def get_chart_recommendation(df: pd.DataFrame) -> tuple[str | None, str | None, str | None]:
    """
    Recommend a chart type and axes based on the DataFrame schema.
    """
    cols = df.columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(exclude=['number', 'datetime']).columns
    datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns

    if len(categorical_cols) == 1 and len(numeric_cols) > 1:
        return "Bar", categorical_cols[0], numeric_cols[0]
    elif len(numeric_cols) == 1 and len(categorical_cols) == 1:
        return "Bar", categorical_cols[0], numeric_cols[0]
    elif len(numeric_cols) == 1 and len(datetime_cols) == 1:
        return "Line", datetime_cols[0], numeric_cols[0]
    elif len(numeric_cols) == 2:
        return "Scatter", numeric_cols[0], numeric_cols[1]
    elif len(numeric_cols) > 2 and len(categorical_cols) == 0:
        return "Heatmap", numeric_cols[0], numeric_cols[1]
    
    return None, None, None

def render_visualization(df: pd.DataFrame, container_key: str = "viz"):
    """Render the visualization layer with optional container scoping.

    Does not mutate the provided DataFrame when applying sorting.
    """
    st.markdown("#### Chart")

    # Guard: no data yet
    if df is None or df.empty:
        st.info("No data to visualize yet.")
        return

    keys, cols = _init_chart_state(df, container_key)

    # Read current selections
    selected_chart = st.session_state.get(keys["chart"], "Bar")
    selected_x = st.session_state.get(keys["x"], cols[0] if cols else None)
    selected_y = st.session_state.get(keys["y"]) if selected_chart != "Histogram" else None
    selected_color = st.session_state.get(keys["color"]) if st.session_state.get(keys["color"]) in ([None] + list(cols)) else None

    # Clamp invalid columns BEFORE widgets render to avoid Streamlit API exceptions
    if cols:
        if selected_x not in cols:
            selected_x = cols[0]
        if selected_chart != "Histogram":
            if selected_y not in cols:
                selected_y = cols[1] if len(cols) > 1 else cols[0]
        # Histogram enforcement: numeric X
        if selected_chart == "Histogram":
            num_cols = list(df.select_dtypes(include=["number"]).columns)
            if selected_x not in num_cols:
                if num_cols:
                    selected_x = num_cols[0]
                else:
                    selected_chart = "Bar"
                    selected_y = cols[1] if len(cols) > 1 else cols[0]
        if selected_color not in ([None] + list(cols)):
            selected_color = None

    # Do not assign widget keys here; widgets may already be instantiated earlier in this run.
    # We'll use session state as-is for widgets and apply clamped values only when building the chart.

    # Sort state
    sort_col_key = f"sort_col_{container_key}"
    sort_dir_key = f"sort_dir_{container_key}"
    default_sort_col = selected_y if (selected_y in cols) else None
    if st.session_state.get(sort_col_key) not in cols + [None]:
        st.session_state[sort_col_key] = default_sort_col
    if sort_dir_key not in st.session_state:
        st.session_state[sort_dir_key] = "Ascending"

    # Controls bound to scoped state keys (compact two-column layout)
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        st.selectbox("Chart type", ALLOWED_CHART_TYPES, index=_safe_index(ALLOWED_CHART_TYPES, selected_chart), key=keys["chart"], help="Choose visualization type")
    with ctrl_col2:
        st.selectbox("X-axis", cols, index=_safe_index(cols, selected_x), key=keys["x"], help="X column")

    # Y is optional for Histogram. Use compact row with Color.
    if st.session_state.get(keys["chart"]) == "Histogram":
        st.caption("Y-axis not required for Histogram (uses count()).")
        y_color_cols = st.columns(2)
        with y_color_cols[0]:
            st.empty()
    else:
        y_color_cols = st.columns(2)
        with y_color_cols[0]:
            st.selectbox("Y-axis", cols, index=_safe_index(cols, selected_y), key=keys["y"], help="Y column")

    color_options = [None] + list(cols)
    with y_color_cols[1]:
        st.selectbox(
            "Color / Group by",
            color_options,
            index=_safe_index(color_options, selected_color),
            key=keys["color"],
            help="Optional grouping",
            format_func=lambda x: "— None —" if x is None else str(x),
        )

    sort_by_options = [None] + list(cols)
    sort_cols = st.columns(2)
    with sort_cols[0]:
        st.selectbox(
            "Sort by",
            sort_by_options,
            index=_safe_index(sort_by_options, st.session_state.get(sort_col_key, default_sort_col)),
            key=sort_col_key,
            help="Sort before plotting",
            format_func=lambda x: "— None —" if x is None else str(x),
        )
    with sort_cols[1]:
        st.selectbox("Sort direction", ["Ascending", "Descending"], key=sort_dir_key)

    # Keep last valid params to avoid disappearing charts on invalid selections
    last_valid_key = f"last_valid_params_{container_key}"

    def _build_and_render(params: dict) -> bool:
        try:
            plot_df = df.copy()
            sort_col = params.get("sort_col")
            sort_dir = params.get("sort_dir", "Ascending")
            if sort_col and sort_col in plot_df.columns:
                # Do not mutate original df; already using copy()
                ascending = (sort_dir == "Ascending")
                try:
                    plot_df = plot_df.sort_values(by=sort_col, ascending=ascending)
                except Exception:
                    # If sorting fails (e.g., mixed types), coerce to string as a last resort
                    plot_df = plot_df.assign(**{sort_col: plot_df[sort_col].astype(str)}).sort_values(by=sort_col, ascending=ascending)

            y_arg = params.get("y")
            if params.get("chart") == "Histogram":
                # Histogram requires numeric X; if not numeric, try to pick one.
                if params.get("x") not in plot_df.select_dtypes(include=["number"]).columns:
                    num_cols = list(plot_df.select_dtypes(include=["number"]).columns)
                    if num_cols:
                        params["x"] = num_cols[0]
                        st.session_state[keys["x"]] = num_cols[0]
                    else:
                        # No numeric columns: fallback to Bar with count by first column
                        params["chart"] = "Bar"
                        params["y"] = None
                y_arg = None

            chart = make_chart(
                plot_df,
                params.get("chart", "Bar"),
                params.get("x", cols[0] if cols else None),
                (None if params.get("chart") == "Histogram" else (y_arg or (cols[1] if len(cols) > 1 else (cols[0] if cols else None)))),
                params.get("color"),
                params.get("sort_col"),
                params.get("sort_dir", "Ascending"),
            )
            if chart is None:
                return False
            st.altair_chart(chart, use_container_width=True)
            return True
        except Exception as e:
            # Show a lightweight note instead of going blank
            st.caption(f"Chart error: {e}")
            return False

    # Collect current selections (auto-correct incompatible state)
    current_params = {
        "chart": st.session_state.get(keys["chart"], "Bar"),
        "x": st.session_state.get(keys["x"], cols[0] if cols else None),
        "y": st.session_state.get(keys["y"]),
        "color": st.session_state.get(keys["color"]),
        "sort_col": st.session_state.get(sort_col_key),
        "sort_dir": st.session_state.get(sort_dir_key, "Ascending"),
    }

    # Auto-fix after chart-type changes: ensure x/y are valid
    if current_params["x"] not in cols:
        current_params["x"] = cols[0]
    if current_params["chart"] == "Histogram":
        current_params["y"] = None
        # Ensure X is numeric for histogram
        if current_params["x"] not in df.select_dtypes(include=["number"]).columns:
            num_cols = list(df.select_dtypes(include=["number"]).columns)
            if num_cols:
                current_params["x"] = num_cols[0]
            else:
                # Fall back to Bar if no numeric columns
                current_params["chart"] = "Bar"
    else:
        if current_params["y"] not in cols:
            # Prefer second column for Y if available
            fallback_y = cols[1] if len(cols) > 1 else cols[0]
            current_params["y"] = fallback_y
    # Keep sort-by aligned with Y by default when unset/invalid
    if current_params["sort_col"] not in cols and current_params["y"] in cols:
        current_params["sort_col"] = current_params["y"]

    # Validate minimal requirements (after auto-fix this should be True)
    valid = True
    if current_params["x"] not in cols:
        valid = False
    if current_params["chart"] != "Histogram" and (current_params["y"] not in cols):
        valid = False

    if valid and _build_and_render(current_params):
        st.session_state[last_valid_key] = current_params
    else:
        # Fallback to last valid params if available
        fallback = st.session_state.get(last_valid_key)
        if fallback and _build_and_render(fallback):
            st.info("Showing last valid chart while current selection is incompatible.")
        else:
            # Final safety net: build a simple recommended chart so UI never goes blank
            rec_chart, rec_x, rec_y = get_chart_recommendation(df)
            if rec_chart is None:
                # Construct a minimal default
                cols_list = list(df.columns)
                if len(cols_list) >= 2:
                    rec_chart, rec_x, rec_y = "Bar", cols_list[0], cols_list[1]
                elif len(cols_list) == 1:
                    rec_chart, rec_x, rec_y = "Histogram", cols_list[0], None
            safe_params = {
                "chart": rec_chart or "Bar",
                "x": rec_x or (list(df.columns)[0] if len(df.columns) else None),
                "y": None if (rec_chart == "Histogram") else (rec_y or (list(df.columns)[1] if len(df.columns) > 1 else (list(df.columns)[0] if len(df.columns) else None))),
                "color": None,
                "sort_col": rec_y if rec_y in df.columns else None,
                "sort_dir": "Ascending",
            }
            if _build_and_render(safe_params):
                st.session_state[last_valid_key] = safe_params
                st.info("Showing a default chart based on your data.")
            else:
                st.warning("Failed to generate chart. Please select compatible columns.")
                st.dataframe(df)

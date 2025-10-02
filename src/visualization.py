
import streamlit as st
import pandas as pd
import altair as alt

def make_chart(df: pd.DataFrame, chart_type: str, x: str, y: str, color: str | None = None):
    """
    Create an Altair chart based on the given parameters.
    """
    if chart_type == "Bar":
        chart = alt.Chart(df).mark_bar().encode(
            x=x,
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
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(x, bin=True),
            y='count()',
        )
    elif chart_type == "Heatmap":
        chart = alt.Chart(df).mark_rect().encode(
            x=x,
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
    categorical_cols = df.select_dtypes(include=['object']).columns
    datetime_cols = df.select_dtypes(include=['datetime']).columns

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

def render_visualization(df: pd.DataFrame):
    """
    Render the visualization layer.
    """
    st.write("### Visualization")

    chart_type, x_axis, y_axis = get_chart_recommendation(df)

    if chart_type:
        st.write(f"Recommended Chart: **{chart_type}**")
    
    cols = df.columns
    chart_type_options = ["Bar", "Line", "Scatter", "Histogram", "Heatmap"]
    
    selected_chart_type = st.selectbox("Chart type", chart_type_options, index=chart_type_options.index(chart_type) if chart_type else 0)
    
    x_axis_options = cols
    selected_x_axis = st.selectbox("X-axis", x_axis_options, index=x_axis_options.get_loc(x_axis) if x_axis else 0)

    y_axis_options = cols
    selected_y_axis = st.selectbox("Y-axis", y_axis_options, index=y_axis_options.get_loc(y_axis) if y_axis else 1)

    color_options = [None] + list(cols)
    selected_color = st.selectbox("Color / Group by", color_options, index=0)

    try:
        chart = make_chart(df, selected_chart_type, selected_x_axis, selected_y_axis, selected_color)
        if chart:
            st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.warning("Failed to generate chart. Please select compatible columns.")
        st.dataframe(df)

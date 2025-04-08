import plotly.graph_objects as go
import streamlit as st


def create_plotly_risk_gauge(value, max_value=1):
    """
    Creates a Plotly gauge chart to display risk, with input value between 0 and 1.
    Displays values on a scale of 0 to 100 on the gauge.
    """

    # Compute percentage and choose color based on thresholds:
    percentage = value * 100  # Directly use value, as max_value is 1
    if percentage < 35:
        bar_color = st.session_state.color_survivor
    elif percentage < 65:
        bar_color = "orange"
    else:
        bar_color = st.session_state.color_non_survivor

    # Create the indicator.
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,  # Display percentage (0-100)
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': '%',
            'font': {'size': 35}  # Adjust the size as needed
        },
        gauge={
            'axis': {'range': [0, 100]},  # Set gauge range to 0-100
            'bar': {'color': bar_color},
        }
    ))

    # Adjust layout and deactivate interactivity buttons.
    fig.update_layout(
        showlegend=False,
        modebar=dict(remove=['toImage', 'zoom', 'pan', 'select',
                             'zoomIn', 'zoomOut', 'autoScale', 'reset', 'fullscreen']),
        margin=dict(l=0, r=0, t=0, b=10),
        width=250,
        height=90,
    )
    return fig

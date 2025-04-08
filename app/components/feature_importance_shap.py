import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


def create_shap_bar_plot(risk_df):
    """
    Erstellt ein horizontales Balkendiagramm für SHAP-Werte mit angepasster Reihenfolge.
    """
    color_survivor = st.session_state.color_survivor
    color_non_survivor = st.session_state.color_non_survivor

    # Copy and Convert risk_df to numeric
    risk_df_numeric = risk_df.copy()
    risk_df_numeric["Risk Contribution"] = pd.to_numeric(
        risk_df_numeric["Risk Contribution"], errors='coerce')

    # Calculate Sums
    total_risk_increasing = risk_df_numeric[risk_df_numeric["Risk Contribution"]
                                            > 0]["Risk Contribution"].sum()
    total_risk_reducing = risk_df_numeric[risk_df_numeric["Risk Contribution"]
                                          < 0]["Risk Contribution"].sum()

    # New fields: Absolute Value and Color
    risk_df_numeric["Absolute Contribution"] = risk_df_numeric["Risk Contribution"].abs()
    risk_df_numeric["Color"] = risk_df_numeric["Risk Contribution"].apply(
        lambda x: color_non_survivor if x > 0 else color_survivor)

    # Extract others row if present to always show it at the end
    others_df = pd.DataFrame()
    if "Others" in risk_df_numeric["Parameter"].values:
        others_df = risk_df_numeric[risk_df_numeric["Parameter"] == "Others"].copy(
        )
        risk_df_numeric = risk_df_numeric[risk_df_numeric["Parameter"] != "Others"]

    # Create dataframe for the summary rows
    sum_data = pd.DataFrame({
        "Parameter": ["Total Risk Increasing Evidence", "Total Risk Reducing Evidence"],
        "Absolute Contribution": [abs(total_risk_increasing), abs(total_risk_reducing)],
        "Color": [color_non_survivor if total_risk_increasing > 0 else color_survivor,
                  color_non_survivor if total_risk_reducing > 0 else color_survivor],
        "Raw Value": ["", ""],
        "order": [1, 2]
    })

    # Sort the feature values without others decreasing
    df_features = risk_df_numeric.copy()
    df_features = df_features.sort_values(
        "Absolute Contribution", ascending=False)
    # Create a new order column starting with 4, as 3 is used as spacer
    df_features = df_features.reset_index(drop=True)
    df_features["order"] = df_features.index + 4

    # Create a spacer row
    spacer = pd.DataFrame({
        "Parameter": [""],
        "Absolute Contribution": [0],
        "Color": ["white"],
        "Raw Value": [""],
        "order": [3]
    })

    # If Others was available, add it to the end
    if not others_df.empty:
        # Overwrite color and absolute contirbution of others
        others_df["Absolute Contribution"] = others_df["Risk Contribution"].abs()
        others_df["Color"] = others_df["Risk Contribution"].apply(
            lambda x: color_non_survivor if x > 0 else color_survivor)
        max_order = max(df_features["order"].max(
        ), spacer["order"].max(), sum_data["order"].max())
        others_df = others_df.copy().reset_index(drop=True)
        others_df["order"] = max_order + 1

    # Combine all rows in the correct order (sum_data, spacer, df_features with others as last row)
    dataframes = [sum_data, spacer, df_features]
    if not others_df.empty:
        dataframes.append(others_df)

    streamlit_data = pd.concat(dataframes, ignore_index=True)

    # Altair Chart: Use order column for sorting
    chart = alt.Chart(streamlit_data).mark_bar().encode(
        x=alt.X("Absolute Contribution:Q", title="Absolute Contribution"),
        y=alt.Y("Parameter:N", sort=alt.SortField(
            field="order", order="ascending"), title="Parameter"),
        color=alt.Color("Color:N", scale=alt.Scale(
            domain=[color_non_survivor, color_survivor, "white"], range=[color_non_survivor, color_survivor, "white"]), legend=None),
        tooltip=["Parameter", "Absolute Contribution", "Raw Value"]
    ).properties(
        width=600,
        height=400
    )

    return chart

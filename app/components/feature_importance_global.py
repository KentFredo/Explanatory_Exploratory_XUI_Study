import streamlit as st
import altair as alt
import pandas as pd


def format_contribution(x):
    """
    Format contributions as percentages with one decimal.
    For positive values, a plus sign is added.
    """
    if pd.isnull(x):
        return "n/a"
    elif x == 0:
        return "0.0%"
    elif x > 0:
        return f"{x:.1f}%"
    else:
        return f"{x:.1f}%"


def create_global_shap_bar_plot():
    """
    Create a horizontal bar plot for global SHAP values with:
      - Top N slider
      - Optional manual feature inclusion (dropdown shows the formatted contribution)
      - An 'Others' bar is computed for unselected features.
    """

    color = "#F3FFE3"

    df = st.session_state.global_feature_importance.copy()

    # Beautify feature names
    df["feature"] = df["feature"].str.replace("_", " ").str.title()

    # Rename columns for plotting logic.
    # "feature" becomes "Parameter" and "mean_shap_value" becomes "Absolute Contribution"
    df = df.rename(columns={
        "feature": "Parameter",
        "mean_shap_value": "Absolute Contribution"
    })

    # Create a formatted version of the SHAP contribution (in percentage)
    df["Formatted Contribution"] = df["Absolute Contribution"].apply(
        format_contribution)

    # Add other necessary columns
    df["Raw Value"] = ""
    df["Color"] = "#F3FFE3"

    # Sort by importance
    df_sorted = df.sort_values(
        "Absolute Contribution", ascending=False).reset_index(drop=True)

    # UI Layout: slider + multiselect side-by-side
    col1, col2 = st.columns([2, 3])
    with col1:
        top_n = st.slider("Number of top features to display:",
                          min_value=5, max_value=min(len(df), 40),
                          value=min(len(df), 15), step=1)

    # Get top N features
    top_df = df_sorted.iloc[:top_n].copy()
    top_features = set(top_df["Parameter"])

    # Get remaining features
    remaining_df = df_sorted.iloc[top_n:].copy()
    remaining_features = list(remaining_df["Parameter"])

    with col2:
        # Create options as "Parameter (Formatted Contribution)"
        options = {f"{row['Parameter']} ({row['Formatted Contribution']})": row["Parameter"]
                   for idx, row in remaining_df.iterrows()}
        options_list = list(options.keys())
        additional_features = st.multiselect(
            "Add more features to compare:",
            options=options_list,
            default=[]
        )

    # Create DataFrame for manually selected features
    manual_df = remaining_df[remaining_df["Parameter"].isin(
        [options[opt] for opt in additional_features]
    )].copy()
    manual_features = set(manual_df["Parameter"])

    # Exclude top N and manually added from the remaining for "Others"
    excluded_features = top_features.union(manual_features)
    others_df = df_sorted[~df_sorted["Parameter"].isin(excluded_features)]

    # Create "Others" row (aggregated) if there are any remaining features.
    if not others_df.empty:
        others_row = pd.DataFrame([{
            "Parameter": "Others",
            "Absolute Contribution": others_df["Absolute Contribution"].sum(),
            "Formatted Contribution": format_contribution(others_df["Absolute Contribution"].sum()),
            "Raw Value": "",
            "Color": "#F3FFE3"
        }])
    else:
        others_row = pd.DataFrame(
            columns=["Parameter", "Absolute Contribution",
                     "Formatted Contribution", "Raw Value", "Color"]
        )

    # Combine the selected parts (top N and manually added)
    df_plot = pd.concat([top_df, manual_df], ignore_index=True)
    df_plot["order"] = df_plot.index + 1

    # Build Altair chart
    chart = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X("Absolute Contribution:Q",
                title="Mean Absolute Risk Contribution"),
        y=alt.Y("Parameter:N", sort=alt.SortField(
            field="order", order="ascending"), title="Feature"),
        color=alt.Color("Color:N", scale=alt.Scale(domain=[color],
                                                   range=[color]), legend=None),
        tooltip=[
            "Parameter",
            alt.Tooltip("Formatted Contribution:N", title="Risk Contribution")
        ]
    ).properties(
        width=600,
        height=500
    )

    return chart

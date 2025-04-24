import streamlit as st
import pandas as pd
import altair as alt


def format_contribution(x):
    """Format contributions with a sign; 0 becomes 'False' and NaN becomes 'n/a'."""
    if pd.isnull(x):
        return "n/a"
    elif x == 0:
        return "False"
    elif x > 0:
        return f"+{x:.1f}%"
    else:
        return f"{x:.1f}%"


def format_raw_value(val, parameter):
    """
    Format the raw value for specific parameters.
    For parameters that are boolean, 0 becomes "False", 1 becomes "True".
    For parameters that indicate culture results, 0 becomes "Negative", 1 becomes "Positive".
    """
    # If the value is not numeric (or is empty), return it as is.
    try:
        rv = float(val)
    except (ValueError, TypeError):
        return val

    # Canonicalize the parameter name: remove spaces and lowercase.
    param_key = parameter.lower().replace(" ", "")
    bool_params = {"specimen", "diagnosis", "race", "vent",
                   "gender", "severeseasexplicit", "septicshockexplicit"}
    pos_params = {"positiveculturepoe", "bloodculturepositive"}

    if param_key in bool_params:
        return "True" if rv == 1 else ("False" if rv == 0 else val)
    elif param_key in pos_params:
        return "Positive" if rv == 1 else ("Negative" if rv == 0 else val)
    else:
        return val


def create_shap_bar_plot(risk_df):
    """
    Creates an interactive horizontal bar plot for SHAP values with:
      - Only features with |SHAP| > 1 are included.
      - A slider (default value 6) to select the top features.
      - A multiselect widget (sorted by absolute SHAP value) whose options display the feature name followed by its formatted SHAP value.
      - Aggregated "Others" for features not selected.
      - Tooltip displays the formatted risk value (renamed as "Risk Value")
        and the actual patient (raw) value formatted for specific parameters.
    """
    # Get colors from session state
    color_survivor = st.session_state.color_survivor
    color_non_survivor = st.session_state.color_non_survivor

    # Copy the dataframe and convert risk contributions to numeric.
    risk_df_numeric = risk_df.copy()
    risk_df_numeric["Risk Contribution"] = pd.to_numeric(
        risk_df_numeric["Risk Contribution"], errors='coerce')

    # If "Raw Value" is not in the dataframe, create it from Risk Contribution.
    if "Raw Value" not in risk_df_numeric.columns:
        risk_df_numeric["Raw Value"] = risk_df_numeric["Risk Contribution"]

    # Beautify the feature names: replace underscores with spaces and title-case them.
    risk_df_numeric["Parameter"] = risk_df_numeric["Parameter"].astype(
        str).str.replace("_", " ").str.title()

    # Compute absolute contribution and create a formatted version of the contribution.
    risk_df_numeric["Absolute Contribution"] = risk_df_numeric["Risk Contribution"].abs()
    risk_df_numeric["Formatted Contribution"] = risk_df_numeric["Risk Contribution"].apply(
        format_contribution)

    # Assign bar colors based on the sign of risk contribution.
    risk_df_numeric["Color"] = risk_df_numeric["Risk Contribution"].apply(
        lambda x: color_non_survivor if x > 0 else color_survivor)

    # Remove any pre‐existing "Others" row so it can be recomputed.
    risk_df_numeric = risk_df_numeric[risk_df_numeric["Parameter"] != "Others"]

    # Compute totals from the filtered set.
    total_risk_increasing = risk_df_numeric[risk_df_numeric["Risk Contribution"]
                                            > 0]["Risk Contribution"].sum()
    total_risk_reducing = risk_df_numeric[risk_df_numeric["Risk Contribution"]
                                          < 0]["Risk Contribution"].sum()

    sum_data = pd.DataFrame({
        "Parameter": ["Total Risk Increasing Evidence", "Total Risk Reducing Evidence"],
        "Absolute Contribution": [abs(total_risk_increasing), abs(total_risk_reducing)],
        "Color": [
            color_non_survivor if total_risk_increasing > 0 else color_survivor,
            color_non_survivor if total_risk_reducing > 0 else color_survivor
        ],
        "Formatted Contribution": [
            format_contribution(total_risk_increasing),
            format_contribution(total_risk_reducing)
        ],
        "Raw Value": ["", ""],
        "order": [1, 2]
    })

    # Sort features in descending order by absolute contribution.
    df_features_sorted = risk_df_numeric.sort_values(
        "Absolute Contribution", ascending=False).reset_index(drop=True)

    # Only include features features where |SHAP| > 1 in df_features_sorted.
    df_features_sorted = df_features_sorted[df_features_sorted["Absolute Contribution"] > 1]

    # --- Interactive selection ---
    # Layout for slider and multiselect.
    col1, col2 = st.columns([2, 3])
    with col1:
        top_n = st.slider(
            "Number of top features to display:",
            min_value=1,
            max_value=min(len(df_features_sorted), 40),
            value=6,  # Default is 6 features.
            step=1
        )

    # Select the top-N features.
    top_df = df_features_sorted.iloc[:top_n].copy()
    top_features_set = set(top_df["Parameter"])

    # Remaining features beyond the top-N.
    remaining_df = df_features_sorted.iloc[top_n:].copy()

    # Prepare multiselect options: sorted descending; each option is "Parameter (Formatted Contribution)".
    options = {f"{row['Parameter']} ({row['Formatted Contribution']})": row["Parameter"]
               for idx, row in remaining_df.iterrows()}
    options_list = list(options.keys())

    with col2:
        selected_options = st.multiselect(
            "Add more features to compare:",
            options_list,
            default=[]
        )

    # Get additional features from the multiselect.
    additional_features = [options[opt] for opt in selected_options]
    manual_df = remaining_df[remaining_df["Parameter"].isin(
        additional_features)].copy()

    # Features that are selected either by top slider or manually.
    selected_features = top_features_set.union(
        set(manual_df["Parameter"].tolist()))

    # --- Aggregated "Others" row ---
    # For all features not selected, create an aggregated bar.
    others_features_df = df_features_sorted[~df_features_sorted["Parameter"].isin(
        selected_features)]
    if not others_features_df.empty:
        aggregated_abs = others_features_df["Absolute Contribution"].sum()
        aggregated_net = others_features_df["Risk Contribution"].sum()
        others_color = color_non_survivor if aggregated_net > 0 else color_survivor
        others_formatted = format_contribution(aggregated_net)
        others_row = pd.DataFrame([{
            "Parameter": "Others",
            "Absolute Contribution": aggregated_abs,
            "Formatted Contribution": others_formatted,
            "Raw Value": aggregated_net,
            "Color": others_color
        }])
    else:
        others_row = pd.DataFrame(columns=[
                                  "Parameter", "Absolute Contribution", "Formatted Contribution", "Raw Value", "Color"])

    # --- Assemble the final DataFrame for plotting ---
    # Combine the interactive features (top and manually selected) and assign orders.
    df_interactive = pd.concat([top_df, manual_df], ignore_index=True).copy()
    # Orders start after summary rows and a spacer.
    df_interactive["order"] = df_interactive.index + 4

    # Spacer row (order 3) for visual separation.
    spacer = pd.DataFrame({
        "Parameter": [""],
        "Absolute Contribution": [0],
        "Formatted Contribution": [""],
        "Color": ["white"],
        "Raw Value": [""],
        "order": [3]
    })

    # Set the order for the "Others" row if it exists.
    if not others_row.empty:
        max_order = max(df_interactive["order"].max(
        ), spacer["order"].max(), sum_data["order"].max())
        others_row = others_row.copy()
        others_row["order"] = max_order + 1

    # Combine all rows: summary rows, spacer, interactive feature rows, and aggregated Others.
    final_df = pd.concat(
        # Excluded Others Row here
        [sum_data, spacer, df_interactive], ignore_index=True)

    # --- Format the "Raw Value" column for specific parameters ---
    final_df["Raw Value"] = final_df.apply(
        lambda row: format_raw_value(
            row["Raw Value"], row["Parameter"]) if row["Raw Value"] != "" else row["Raw Value"],
        axis=1
    )

    # --- Determine chart height based on the number of selected features ---
    n_selected = len(selected_features)
    if n_selected >= 15:
        chart_height = 700
    elif n_selected > 10:
        chart_height = 600
    else:
        chart_height = 500

    # --- Build the Altair chart ---
    chart = alt.Chart(final_df).mark_bar().encode(
        x=alt.X("Absolute Contribution:Q", title="Absolute Contribution"),
        y=alt.Y("Parameter:N", sort=alt.SortField(
            field="order", order="ascending"), title="Parameter"),
        color=alt.Color(
            "Color:N",
            scale=alt.Scale(
                domain=[color_non_survivor, color_survivor, "white"],
                range=[color_non_survivor, color_survivor, "white"]
            ),
            legend=None
        ),
        tooltip=[
            "Parameter",
            alt.Tooltip("Formatted Contribution:N", title="Risk Value"),
            "Raw Value"
        ]
    ).properties(
        width=600,
        height=chart_height
    )

    return chart

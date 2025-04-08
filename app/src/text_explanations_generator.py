import streamlit as st
import pandas as pd
import numpy as np


def generate_clinical_interpretation(patient_risk, shap_group_contributions):
    """
    Generate a clinical interpretation based on SHAP values, static feature names, and patient values.
    """

    # Define risk level and color
    risk_level = (
        "low" if patient_risk < 0.25
        else "moderate" if patient_risk < 0.5
        else "elevated" if patient_risk < 0.75
        else "high"
    )
    risk_color = {
        "low": "#2ECC71",
        "moderate": "#F4D03F",
        "elevated": "#E67E22",
        "high": "#E74C3C"
    }[risk_level]

    # Build DataFrame of individual SHAP values
    df = pd.DataFrame({
        "Feature": st.session_state.static_feature_names,
        # Use the 'static' key here
        "SHAP Value": st.session_state.shap_values["static"],
        "Raw Value": [st.session_state.patient.get_feature_value(f) for f in st.session_state.static_feature_names]
    })

    df["SHAP Value"] = pd.to_numeric(df["SHAP Value"], errors="coerce")
    df = df.dropna(subset=["SHAP Value"])
    df = df.sort_values(by="SHAP Value", key=np.abs, ascending=False)

    # Group logic: select up to 3 top contributors based on a 75% threshold of the top value
    def top_contributors(contributions_dict, threshold_ratio=0.75, max_items=3):
        sorted_items = sorted(contributions_dict.items(),
                              key=lambda x: abs(x[1]), reverse=True)
        if not sorted_items:
            return []
        top_items = [sorted_items[0]]
        first_val = abs(sorted_items[0][1])
        for item in sorted_items[1:]:
            if abs(item[1]) >= threshold_ratio * first_val and len(top_items) < max_items:
                top_items.append(item)
        return top_items

    # Exclude groups that are not actual clinical categories (e.g., "Risk Increasing Evidence", etc.) if needed
    # For example, you might filter them out here:
    valid_groups = {k: v for k, v in shap_group_contributions.items(
    ) if k not in ["Risk ↑ Evidence", "Risk ↓ Evidence"]}

    # Split into positive/negative group contributions from valid groups
    pos_groups = {k: v for k, v in valid_groups.items() if v > 0}
    neg_groups = {k: v for k, v in valid_groups.items() if v < 0}

    top_pos_groups = top_contributors(pos_groups)
    top_neg_groups = top_contributors(neg_groups)

    # Split into top positive/negative individual features
    top_positive_feats = df[df["SHAP Value"] > 0]
    top_negative_feats = df[df["SHAP Value"] < 0]

    # Apply the threshold for positive features
    if not top_positive_feats.empty:
        top_positive_feats = top_positive_feats[top_positive_feats["SHAP Value"]
                                                >= 0.75 * top_positive_feats["SHAP Value"].iloc[0]].head(3)
    # And for negative features
    if not top_negative_feats.empty:
        top_negative_feats = top_negative_feats[top_negative_feats["SHAP Value"]
                                                <= 0.75 * top_negative_feats["SHAP Value"].iloc[0]].head(3)

    # Helper to format feature names
    def format_name(name):
        return name.replace("_", " ").title()

    # Build the interpretation text
    text = (
        f"The patient's predicted mortality risk is "
        f"<span style='color:{risk_color};'><strong>{risk_level.upper()} ({patient_risk:.0%})</strong></span>. "
    )

    if top_pos_groups:
        groups_str = ", ".join(
            [f"{g[0]} (impact score: +{abs(g[1]):.2f})" for g in top_pos_groups])
        text += f"The strongest contributing factor category is {groups_str}. "
    else:
        text += "No category significantly increased the risk. "

    if top_neg_groups:
        groups_str = ", ".join(
            [f"{g[0]} (impact score: -{abs(g[1]):.2f})" for g in top_neg_groups])
        text += f"Risk reduction was mainly due to {groups_str}. "
    else:
        text += "No category significantly reduced the risk. "

    if not top_positive_feats.empty:
        feats_str = ", ".join(
            [f"{format_name(r['Feature'])} ({r['Raw Value']})" for _, r in top_positive_feats.iterrows()])
        text += f"Notably, {feats_str} significantly increased the predicted risk. "
    else:
        text += "No single feature drastically increased the risk. "

    if not top_negative_feats.empty:
        feats_str = ", ".join(
            [f"{format_name(r['Feature'])} ({r['Raw Value']})" for _, r in top_negative_feats.iterrows()])
        text += f"In contrast, {feats_str} helped reduce the risk."
    else:
        text += "No single feature drastically decreased the risk."

    return text

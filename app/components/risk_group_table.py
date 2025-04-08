import streamlit as st
import pandas as pd


def render_local_group_shap_table(risk_type, shap_dict):
    """Renders a detailed risk table without an expander, with colored values and arrows."""

    risk_inc_value = st.session_state.shap_group_contributions.get(
        'Risk ↑ Evidence', 0.0)
    risk_dec_value = st.session_state.shap_group_contributions.get(
        'Risk ↓ Evidence', 0.0)
    color_non_survivor = st.session_state.color_non_survivor
    color_survivor = st.session_state.color_survivor

    if risk_type == "inc":
        title = f"Risk <span style='color: {color_non_survivor};'>↑</span> Evidence: <span style='color: {color_non_survivor};'>{risk_inc_value:+.2f}</span>"
        description_text = "These clinical categories most increased the patient's risk prediction."
        color = color_non_survivor
        arrow_up_html = f"<span style='color: {color};'>↗</span>"
        arrow_down_html = ""
    elif risk_type == "dec":
        title = f"Risk <span style='color: {color_survivor};'>↓</span> Evidence: <span style='color: {color_survivor};'>{risk_dec_value:+.2f}</span>"
        description_text = "These clinical categories most helped reduce the predicted risk."
        color = color_survivor
        arrow_up_html = ""
        arrow_down_html = f"<span style='color: {color};'>↘</span>"
    else:
        st.error(f"Invalid risk_type: {risk_type}. Must be 'inc' or 'dec'.")
        return

    st.markdown(f"#### {title}", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size: 0.80em; color: #AAAAAA;'>{description_text}</div>",
        unsafe_allow_html=True
    )

    # Inject CSS styling (always shown)
    st.markdown(f"""
    <style>
    .custom-table-no-expander {{
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9em;
    }}
    .custom-table-no-expander th {{
        text-align: left;
        padding: 8px 6px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        font-weight: bold;
        border-bottom: 1px solid #444;
    }}
    .custom-table-no-expander td {{
        padding: 6px 10px;
        border: none;
        border-bottom: 1px solid #222;
    }}
    .custom-table-no-expander td:last-child {{
        text-align: right;
        color: {color};
    }}
    .custom-table-no-expander .empty-message td {{
        color: #AAAAAA;
        font-style: italic;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Start building the table
    table_html = f"<table class='custom-table-no-expander'>"
    table_html += "<tr><th>Categories</th><th>Risk Value</th></tr>"

    if shap_dict:
        sorted_items = sorted(
            shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
        for group, value in sorted_items:
            arrow_html = ""
            value_color = color
            if value > 0:
                arrow_html = arrow_up_html
            elif value < 0:
                arrow_html = arrow_down_html

            table_html += f"<tr><td>{group}</td><td style='text-align: right; color: {value_color};'>{value:+.2f} {arrow_html}</td></tr>"
    else:
        table_html += "<tr class='empty-message'><td colspan='2'>No major contributing factors found for this category.</td></tr>"

    table_html += "</table>"

    # Display the table
    st.markdown(table_html, unsafe_allow_html=True)


def render_local_detail_shap_table(risk_df, color_positive="#FF4B4B", color_negative="#00C853", top_n=5):
    """Renders a detailed risk table with the top N parameters, their values, contributions, and explanations with sign and arrow."""
    st.markdown("#### Most Influential Clinical Parameters")
    st.markdown(
        "<div style='font-size: 0.80em; color: #AAAAAA;'>The top individual clinical parameters influencing the predicted risk.</div>",
        unsafe_allow_html=True
    )

    if risk_df.empty:
        st.markdown("<div style='font-size: 0.9em; color: #AAAAAA; font-style: italic;'>No significant individual risk factors to display.</div>", unsafe_allow_html=True)
        return

    top_df = risk_df.head(top_n).copy()

    if len(risk_df) > top_n:
        others_sum = risk_df.iloc[top_n:]["Risk Contribution"].astype(
            float).sum()
        others_row = {
            "Parameter": "Others",
            "Raw Value": "",
            "Risk Contribution": f"{others_sum:.2f}",
            "Description": "<div style='font-size: 0.9em; '>Combined contribution of other less influential parameters.</div>",
            "Comparison": ""
        }
        others_df = pd.DataFrame([others_row])
        display_df = pd.concat([top_df, others_df], ignore_index=True)
    else:
        display_df = top_df.copy()

    # Define the HTML for the table with the specified styling
    table_html = f"""
    <style>
    .detailed-risk-table {{
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9em;
    }}
    .detailed-risk-table th {{
        text-align: left;
        padding: 8px 6px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        font-weight: bold;
        border-bottom: 1px solid #444;
    }}
    .detailed-risk-table td {{
        padding: 6px 10px;
        border: none;
        border-bottom: 1px solid #222;
    }}
    .detailed-risk-table td:nth-child(3) {{ /* Style for Risk Contribution */
        text-align: right;
        min-width: 80px; /* Adjust this value as needed */
    }}
    .description-cell {{
        font-size: 0.9em; /* Adjust the size for the main description */
    }}
    .comparison-text {{
        font-size: 0.85em;
        color: #AAAAAA;
        padding-left: 10px; /* Add a left padding for indentation */
    }}
    </style>
    <table class='detailed-risk-table'>
        <tr><th>Parameter</th><th>Value</th><th>Risk Value</th><th>Details</th></tr>
    """
    for index, row in display_df.iterrows():
        parameter_name = row['Parameter'].replace("_", " ").title()
        contribution = float(row['Risk Contribution'])
        contribution_color = color_positive if contribution > 0 else color_negative
        contribution_str = f"{contribution:+.2f}"

        arrow = ""
        if contribution > 0:
            arrow = "↗"  # Upwards arrow
        elif contribution < 0:
            arrow = "↘"  # Downwards arrow
        else:
            arrow = "→"  # Sideways arrow

        table_html += f"<tr><td>{parameter_name}</td><td>{row['Raw Value']}</td><td style='color: {contribution_color}; text-align: right;'>{contribution_str} {arrow}</td><td class='description-cell'>{row['Description']}<div class='comparison-text'>{row['Comparison']}</div></td></tr>"
    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)

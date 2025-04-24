import streamlit as st
from components.feature_importance_shap import create_shap_bar_plot
from components.risk_group_table import render_local_group_shap_table


def show_feature_importance_local():
    st.markdown("#### What influenced this patient's risk?")
    with st.expander(
        "What does this chart show?",
        expanded=False,
        icon=":material/help:",
    ):
        st.markdown(
            """
            <div style='font-size: 0.85em'>
            This chart displays the features that contributed most to <strong>this patient’s predicted risk</strong>, with interactive options to customize the view.
            <br><br>
            <strong>How to read the plot:</strong>
            <ul>
                <li>The <strong>top two bars</strong> summarize the overall influence:
                    <ul>
                        <li><strong>Risk Increasing Evidence</strong> 🔴: The combined impact of all features that increased the risk.</li>
                        <li><strong>Risk Decreasing Evidence</strong> 🔵: The combined impact of all features that decreased the risk.</li>
                    </ul>
                </li>
                <li>The <strong>individual bars below</strong> show the specific impact of each feature:
                    <ul>
                        <li>Longer bars indicate a stronger influence on the risk.</li>
                        <li>🔴 Red bars indicate features that pushed the risk higher.</li>
                        <li>🔵 Blue bars indicate features that pulled the risk lower.</li>
                    </ul>
                </li>
                <li><strong>Interactive options:</strong>
                    <ul>
                        <li><strong>Slider:</strong> Adjust the number of top features to display.</li>
                        <li><strong>Dropdown:</strong> Select additional features from a sorted list where each entry shows the feature name followed by its formatted risk value.</li>
                    </ul>
                </li>
            </ul>
            <br>
            <strong>Use this page to:</strong>
            <ul>
                <li>Understand which factors are pushing the patient's risk up or down.</li>
                <li>Identify the most influential clinical factors along with the underlying patient data.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Generate and display the SHAP bar plot
    risk_df = st.session_state.sepsis_prediction_model.create_risk_table(
        shorten_table=False)

    # Filter out summary categories from the breakdown
    filtered_contributions = {
        k: v for k, v in st.session_state.shap_group_contributions.items()
        if k not in ['Risk ↑ Evidence', 'Risk ↓ Evidence']
    }

    # Sort the contributions once and pass them directly
    sorted_increasing = dict(sorted(
        ((k, v) for k, v in filtered_contributions.items() if v > 0),
        key=lambda x: abs(x[1]),
        reverse=True
    ))

    sorted_decreasing = dict(sorted(
        ((k, v) for k, v in filtered_contributions.items() if v < 0),
        key=lambda x: abs(x[1]),
        reverse=True
    ))

    group_shap_col, detail_shap_col = st.columns([1, 2.5], gap='large')
    with group_shap_col:
        render_local_group_shap_table(
            risk_type="inc",
            shap_dict=sorted_increasing,
        )

        render_local_group_shap_table(
            risk_type="dec",
            shap_dict=sorted_decreasing,
        )
    with detail_shap_col:
        shap_chart = create_shap_bar_plot(risk_df)
        # Show the chart
        st.altair_chart(shap_chart, use_container_width=True)

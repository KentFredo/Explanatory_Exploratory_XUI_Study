import streamlit as st
from components.feature_importance_shap import create_shap_bar_plot


def show_feature_importance_local():
    st.markdown("#### What influenced this patient's risk?")
    with st.expander(
        "What does this chart show?",
        expanded=False,
        icon=":material/help:",
    ):
        st.markdown(
            """
            This chart shows which features contributed most to **this patient’s predicted risk**.

            **How to read the plot:**
            - The **top two bars** summarize the total influence:
                - **Risk Increasing Evidence** (red): Sum of all features that pushed the risk higher.
                - **Risk Decreasing Evidence** (blue): Sum of all features that pulled the risk lower.
            - The **individual bars below** show each feature's specific impact.
                - Longer bars indicate stronger influence.
                - Red bars *increased* the predicted risk.
                - Blue bars *decreased* the predicted risk.

            **Use this page to:**
            - See what pushed the patient's risk up or down.
            - Identify the most influential clinical factors.
            """
        )
    # Generate and display the SHAP bar plot
    risk_df = st.session_state.sepsis_prediction_model.create_risk_table()
    shap_chart = create_shap_bar_plot(risk_df)
    # Show the chart
    st.altair_chart(shap_chart, use_container_width=True)

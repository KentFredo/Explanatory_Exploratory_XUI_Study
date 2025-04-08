import streamlit as st
from components.feature_importance_global import create_global_shap_bar_plot


def show_feature_importance_global():
    st.markdown("#### What generally influences risk predictions?")
    with st.expander(
        "What does this chart show?",
        expanded=False,
        icon=":material/help:",
    ):
        st.markdown(
            """
            This chart shows which features were **most influential across all patients** when predicting risk.

            **How to read the plot:**
            - The bars represent the **average contribution** of each feature to the model’s predictions.
            - **Longer bars** indicate that a feature had a **stronger influence** on predicted risk.
            - This view reflects the model’s behavior over the entire dataset—not just for one individual.

            **Use this page to:**
            - Understand what factors the model considers most important overall.
            - Gain insight into the key drivers of risk in the patient population.
            """
        )

    # Show the chart
    chart = create_global_shap_bar_plot()
    st.altair_chart(chart, use_container_width=True)

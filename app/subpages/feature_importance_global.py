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
            <div style='font-size: 0.85em'>
            This chart shows which features were <strong>most influential across all patients</strong> when predicting risk.
            <br><br>
            <strong>How to read the plot:</strong>
            <ul>
            <li>The bars represent the <strong>average (absolute) contribution</strong> of each feature to the model’s predictions.</li>
            <li><strong>Longer bars</strong> indicate that a feature had a <strong>stronger influence</strong> on predicted risk.</li>
            <li><strong>Note:</strong> The values shown are absolute contributions, which means they indicate the magnitude of the effect but not its direction. For example, a value of 2.4 for a feature like "Vent" suggests that it had a strong influence—this influence could have either increased or decreased the overall risk.</li>
            </ul>
            <br>
            <strong>Use this page to:</strong>
            <ul>
            <li>Understand which factors the model considers most important overall.</li>
            <li>Gain insight into the key drivers of risk in the patient population, regardless of whether those features are pushing the risk higher or lower.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Show the chart
    chart = create_global_shap_bar_plot()
    st.altair_chart(chart, use_container_width=True)

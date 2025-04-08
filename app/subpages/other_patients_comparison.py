import streamlit as st
from components.parallel_feature_plot import create_parallel_feature_plot


def show_other_patients_comparison():
    st.markdown("#### Compare to Typical Patients")
    with st.expander(
        "What does this chart show?",
        expanded=False,
        icon=":material/help:",
    ):
        st.markdown(
            """
            This chart compares the selected patient's clinical features with typical values seen in survivors and non-survivors from the training dataset.

            **How to read the plot:**
            - Each dot represents a value for a selected feature.
            - Lines connect the values for each group: **Patient**, **Survivor**, and **Non-Survivor**.
            - Hover over a point to see exact values and the typical range.
            
            **Use this page to:**
            - Understand which features make this patient more similar to survivors or non-survivors.
            - Identify outliers or red flags in the patient's profile.
            """
        )
    parallel_feature_plot = create_parallel_feature_plot()
    st.altair_chart(parallel_feature_plot,
                    use_container_width=True)

    with st.expander("Dataset Overview (Table One-style)", expanded=False):
        st.markdown("This Table shows basically table one.")
        st.dataframe()

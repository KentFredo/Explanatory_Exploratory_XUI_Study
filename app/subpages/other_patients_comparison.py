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
            <div style='font-size: 0.85em'>
            This chart compares the selected patient's clinical features with typical values seen in survivors and non-survivors from the training dataset as well as reference ranges.
            <br><br>
            <strong>How to read the plot:</strong>
            <ul>
                <li>Each dot represents a value for a selected feature.</li>
                <li>Lines connect the values for each group: <strong>Patient</strong>, <strong>Survivor</strong>, and <strong>Non-Survivor</strong>.</li>
                <li>Hover over a point to see exact values and the typical range.</li>
            </ul>
            <br>
            <strong>Use this page to:</strong>
            <ul>
                <li>Understand which features make this patient more similar to survivors or non-survivors.</li>
                <li>Identify outliers or red flags in the patient's profile.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    parallel_feature_plot = create_parallel_feature_plot()
    st.altair_chart(parallel_feature_plot,
                    use_container_width=True)

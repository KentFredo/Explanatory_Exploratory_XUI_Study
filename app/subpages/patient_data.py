import streamlit as st
import pandas as pd
from components.trend_graph import generate_trend_graph
from components.patient_details import create_patient_tile


def display_patient_data():
    # Reduce the spacing at the top of the page
    st.markdown(
        """
        <style>
        /* Override the padding of the main content container */
        .stMainBlockContainer {
            padding-top: 60px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    def build_scores_box(score_name, score_value, score_max_value):
        st.metric(
            label=score_name,
            value=f"{score_value}/{score_max_value}",
            help=f"Maximum Value: {score_max_value}",
        )

    def build_diagnosis_badges(diagnosis_data):
        badges = ""
        for key, value in diagnosis_data.items():
            if value == 1:
                badges = badges + (f":blue-badge[{key}] ")

        return badges

    def build_specimen_badges(specimen_data):
        badges = ""
        for key, value in specimen_data.items():
            if value == 1:
                display_key = key.replace("_", " ").title()
                badges = badges + (f":blue-badge[{display_key}] ")
        return badges

    pat_demographics_col, diagnosis_col, scores_col, infection_col = st.columns([
        1, 1.6, 1.3, 1.6], border=True)

    with pat_demographics_col:
        create_patient_tile()

    with diagnosis_col:
        st.markdown("#### Diagnosis")
        # Evaluate sepsis conditions and prepare an alarm only if necessary.
        severe_sepsis = st.session_state.patient.clinical_data.get(
            "severe_sepsis_explicit")
        septic_shock = st.session_state.patient.clinical_data.get(
            "septic_shock_explicit")

        alarm_text = None
        if septic_shock in [True, 1]:
            background = "#ff6767"  # Pastel red
            alarm_text = f"! SEPTIC SHOCK evaluated !"
        elif severe_sepsis in [True, 1]:
            background = "#ffdf80"  # Pastel yellow
            alarm_text = f"! SEVERE SEPSIS evaluated !"

        # Only display the alarm if one is present.
        if alarm_text:
            st.markdown(
                f"""
                <div style="
                    width:100%;
                    margin: 0 0 1rem 0;
                    padding: 0.1rem;
                    background-color: {background};
                    border-radius:5px;
                    text-align: center;
                    font-size: 0.9rem;
                    font-weight: bold;
                    color: white;
                ">
                    {alarm_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        diagnosis_header_col, diagnois_badge_col = st.columns(
            [1, 2], gap="small")
        with diagnosis_header_col:
            st.caption("Category:")
        with diagnois_badge_col:
            diagnosis_badges = build_diagnosis_badges(
                st.session_state.patient.diagnosis)
            st.markdown(diagnosis_badges)

        st.markdown(
            """
            <div style="margin: 0; padding: 0;">
                <hr style="margin: 0;">
            </div>
            """,
            unsafe_allow_html=True
        )
        vent_header_col, vent_val_col = st.columns([1, 2], gap="small")
        with vent_header_col:
            st.caption("Ventilated:")
        with vent_val_col:
            ventilated = st.session_state.patient.clinical_data.get(
                "vent")
            if ventilated in [True, 1]:
                vent_text = "True"
                st.markdown(f":blue-badge[{vent_text}]")
            else:
                vent_text = "False"
                st.markdown(f":grey-badge[{vent_text}]")

    with scores_col:
        st.markdown("#### Scores")
        left_scores_col, right_scores_col = st.columns(2)
        with left_scores_col:
            build_scores_box(
                "SOFA", int(st.session_state.patient.scores['sofa']), 20)
            build_scores_box(
                "GCS", int(st.session_state.patient.scores['mingcs']), 15)

        with right_scores_col:
            build_scores_box(
                "SIRS", int(st.session_state.patient.scores['sirs']), 5)
            build_scores_box("Elixhauser",
                             int(st.session_state.patient.scores['elixhauser_hospital']), 10)

    with infection_col:
        with st.container():
            st.markdown("#### Infection")
            # Get all data for the infection section
            infection_time = st.session_state.patient.clinical_data.get(
                "suspected_infection_time_poe_days")
            if infection_time is None:
                infection_time = "???"

            # Structure for infection time information
            infection_time_header_col, infection_time_col = st.columns([1, 1])

            with infection_time_header_col:
                st.caption(
                    "Infection Time:")

            with infection_time_col:
                st.markdown(
                    f":grey-badge[{infection_time} days]", unsafe_allow_html=True)

            # Strucutre for the infection test results
            positive_culture_poe = st.session_state.patient.clinical_data.get(
                "positiveculture_poe")
            if positive_culture_poe in [True, 1]:
                badge = ':red-badge[POSITIVE]'
            else:
                badge = ':grey-badge[NEGATIVE]'
            st.markdown(f"###### Tests: {badge}", unsafe_allow_html=True)

            specimen_header_col, specimen_col = st.columns([1, 1])
            with specimen_header_col:
                st.caption(
                    "Specimen:")
            with specimen_col:
                specimen_badges = build_specimen_badges(
                    st.session_state.patient.specimen)
                st.markdown(specimen_badges)

            blood_culture_header_col, blood_culture_col = st.columns(
                [1, 1])
            with blood_culture_header_col:
                st.caption("Blood Culture:")
            with blood_culture_col:
                blood_culture = st.session_state.patient.clinical_data.get(
                    "blood_culture_positive")
                if blood_culture in [True, 1]:
                    blood_culture_text = "Positive"
                    st.markdown(f":red-badge[{blood_culture_text}]")
                else:
                    blood_culture_text = "Negative"
                    st.markdown(f":grey-badge[{blood_culture_text}]")

    # Build the 2nd row of values on the page
    lab_table_col, trends_col = st.columns([3, 3], border=True)

    with lab_table_col:
        with st.container(border=False):
            st.markdown("#### Laboratory Values")
            if not st.session_state.patient.laboratory.empty:
                # Create a copy so you don't modify the original DataFrame.
                lab_df = st.session_state.patient.laboratory.copy()

                # Convert column headers to title case.
                lab_df.columns = lab_df.columns.str.title()

                # If the index is of object type, convert it to title case.
                if lab_df.index.dtype == 'object':
                    lab_df.index = lab_df.index.str.title()

                # If a "Slope" column exists, create a "Trend" column with an arrow.
                if "Slope" in lab_df.columns:
                    def arrow_formatter(x):
                        if pd.isna(x):
                            return ""
                        elif x > 0:
                            return "▲"  # positive slope: arrow up
                        elif x < 0:
                            return "▼"  # negative slope: arrow down
                        else:
                            return "►"  # zero slope: arrow right

                    lab_df["Trend"] = lab_df["Slope"].apply(arrow_formatter)

                # Prepare a format mapping for numeric columns to show 1 decimal place.
                num_cols = lab_df.select_dtypes(include=["number"]).columns
                fmt = {col: "{:.1f}" for col in num_cols}

                # Apply a Pandas Styler to create a LaTeX-style table look.
                lab_styler = (
                    lab_df.style
                    .format(fmt)
                    .set_properties(**{
                        "text-align": "center",
                        "border": "1px solid #ccc",
                        "padding": "0.5rem"
                    })
                    # Set the "Trend" column to a fixed, narrow width.
                    .set_properties(subset=["Trend"], **{
                        "min-width": "30px",
                        "max-width": "30px",
                        "width": "30px"
                    })
                    # Style the header.
                    .set_table_styles([
                        {
                            "selector": "th",
                            "props": [
                                ("font-weight", "bold"),
                                ("text-align", "center"),
                                ("border", "1px solid #ccc"),
                                ("padding", "0.5rem")
                            ]
                        }
                    ])
                )

                st.dataframe(lab_styler)
            else:
                st.write("No laboratory data available.")

    with trends_col:
        trends_chart = generate_trend_graph()
        st.altair_chart(trends_chart, use_container_width=True)

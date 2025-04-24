import streamlit as st
import pandas as pd
import numpy as np
from components.trend_graph import generate_trend_graph
from components.patient_details import create_patient_tile


def display_patient_data():

    def build_scores_box(score_name, score_value, score_max_value, help_text=None):
        # Display the caption with the score name and tooltip help text
        st.caption(score_name, help=help_text)

        # Format the value so the score_value is larger and the '/score_max_value' is gray and smaller
        formatted_value = (
            # The main score value in a larger, bold font
            f"<span style='font-size:2em; font-weight:bold;'>{score_value}</span> "
            # Gray and smaller max value
            f"<span style='color: grey; font-size: 1em;'>/{score_max_value}</span>"
        )
        # Wrap the formatted value in a div with a negative margin to reduce the space
        st.markdown(
            f"<div style='margin-top: -30px; margin_bottom: 10px;'>{formatted_value}</div>", unsafe_allow_html=True)

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
            [1, 1.5], gap="small")
        with diagnosis_header_col:
            st.caption("Diagnosis Group:",
                       help="Grouped by the affected system or clinical category (e.g., Pulmonary, Renal, Cardiovascular, Other).")
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
        vent_header_col, vent_val_col = st.columns([1, 1.5], gap="small")
        with vent_header_col:
            st.caption(
                "Ventilated:", help="If the patient was ventilated within the first 24 hours of ICU admission.")
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
                "SOFA",
                int(st.session_state.patient.scores['sofa']),
                20,
                help_text="**Sequential Organ Failure Assessment:**  \nEvaluates the function of six organ systems (respiratory, coagulation, hepatic, cardiovascular, neurological, and renal). Higher scores indicate more severe organ dysfunction.  \n\nThis score is based on the most abnormal values recorded during the first 24 hours after ICU admission."
            )
            build_scores_box(
                "GCS",
                int(st.session_state.patient.scores['mingcs']),
                15,
                help_text="**Glasgow Coma Scale:**  \nAssesses a patient's level of consciousness based on eye, verbal, and motor responses. Lower scores correlate with greater impairment.  \n\nThis score is determined from the lowest value measured in the first 24 hours after ICU admission."
            )

        with right_scores_col:
            build_scores_box(
                "SIRS",
                int(st.session_state.patient.scores['sirs']),
                5,
                help_text="**Systemic Inflammatory Response Syndrome:**  \nMeasures the body's inflammatory response using key vital signs and white blood cell count. A higher score suggests a stronger systemic response.  \n\nThis value is derived from the most abnormal results during the first 24 hours after ICU admission."
            )
            build_scores_box(
                "Elixhauser",
                int(st.session_state.patient.scores['elixhauser_hospital']),
                10,
                help_text="**Elixhauser Comorbidity Index:**  \nSummarizes the burden of comorbid conditions from administrative data to help predict patient outcomes and potential complications.  \n\nThis score reflects the severest abnormalities noted in the first 24 hours after ICU admission."
            )

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
                    "Infection Time:", help="Days elapsed from ICU admission until the suspected infection was identified.")

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
                    "Specimen:", help="A biological sample taken (e.g., blood, tissue, urine) collected from a patient for analysis and diagnostic testing.")

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
    lab_table_col, trends_col = st.columns([3.2, 2.8], border=True)

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

                # Add Unit from metadata.
                lab_df["Unit"] = lab_df.index.map(
                    lambda test: st.session_state.feature_metadata.get(
                        test.lower() + "_mean", {}).get("unit", "")
                )

                # Set the index name to "Feature".
                lab_df.index.name = "Feature"

                # Compute a new "Range" column from "Min" and "Max".
                lab_df["Range"] = lab_df.apply(
                    lambda row: f"{row['Min']:.1f} - {row['Max']:.1f}"
                    if pd.notna(row["Min"]) and pd.notna(row["Max"]) else "",
                    axis=1
                )

                # Compute a "Normal Range" column from the metadata.
                def get_normal_range(feature):
                    meta = st.session_state.feature_metadata.get(
                        feature.lower() + "_mean", {})
                    nl = meta.get("normal_lower", "")
                    nu = meta.get("normal_upper", "")
                    # Only return the range if both limits are defined.
                    if pd.isna(nl) or pd.isna(nu) or nl == "" or nu == "":
                        return ""
                    return f"{nl} - {nu}"
                lab_df["Normal Range"] = lab_df.index.map(get_normal_range)

                # Rename "Normal Range" to "Reference".
                lab_df.rename(
                    columns={"Normal Range": "Reference"}, inplace=True)

                # Compute the "Status" based on the "Mean" and the normal range.
                def compute_status(row):
                    mean_val = row["Mean"]
                    meta = st.session_state.feature_metadata.get(
                        row.name.lower() + "_mean", {})
                    try:
                        nl = float(meta.get("normal_lower", np.nan))
                        nu = float(meta.get("normal_upper", np.nan))
                    except (ValueError, TypeError):
                        return ""
                    if pd.isna(mean_val) or pd.isna(nl) or pd.isna(nu):
                        return ""
                    if mean_val < nl:
                        return "Low"
                    elif mean_val > nu:
                        return "High"
                    else:
                        return "Normal"
                lab_df["Status"] = lab_df.apply(compute_status, axis=1)

                # Format "Slope" with arrow indications, if the column exists.
                if "Slope" in lab_df.columns:
                    def format_slope_with_arrow(x):
                        if pd.isna(x):
                            return ""
                        arrow = "►" if x == 0 else ("▲" if x > 0 else "▼")
                        return f"{x:.1f} {arrow}"
                    lab_df["Slope"] = lab_df["Slope"].apply(
                        format_slope_with_arrow)

                # Reorder the columns to: Unit, Mean, Range, Reference, Status, Slope.
                cols_order = ["Unit", "Mean",
                              "Range", "Reference", "Status"]
                if "Slope" in lab_df.columns:
                    cols_order.append("Slope")
                lab_df = lab_df[cols_order]

                # Prepare a format mapping for numeric columns to show 1 decimal place.
                num_cols = lab_df.select_dtypes(include=["number"]).columns
                fmt = {col: "{:.1f}" for col in num_cols}

                # Define a function for status coloring: only set a pastel red for High/Low.
                def highlight_status(val):
                    if val in ["High", "Low"]:
                        return "color: #FF9999"  # Pastel red
                    return ""  # Leave it unchanged

                # Apply a Pandas Styler to create a table with the desired styling.
                lab_styler = (
                    lab_df.style
                    .set_table_styles([
                        # Header styling:
                        {'selector': 'th', 'props': [
                            ('font-weight', 'bold'),
                            ('text-align', 'center'),
                            ('border', '1px solid #ccc'),
                            ('padding', '0.5rem')
                        ]}
                    ])
                    .format(fmt)
                    .set_properties(**{
                        "text-align": "center",
                        "border": "1px solid #ccc",
                        "padding": "0.5rem"
                    })
                    .set_properties(subset=["Slope"], **{
                        "min-width": "30px",
                        "max-width": "30px",
                        "width": "30px",
                        "text-align": "right"
                    })
                    .map(highlight_status, subset=["Status"])
                )

                # Optionally increase the height to show more rows.
                st.dataframe(lab_styler, height=700)
            else:
                st.write("No laboratory data available.")

    with trends_col:
        trends_chart = generate_trend_graph()
        st.altair_chart(trends_chart, use_container_width=True)

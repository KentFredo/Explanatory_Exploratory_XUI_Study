from streamlit_counterfactual_slider import st_counterfactual_slider
import streamlit as st


def show_counterfactual():
    """
    Display the counterfactual explanation.
    """
    st.markdown("#### What if... Analysis")

    with st.expander(
        "What is a Counterfactual Explanation?",
        expanded=False,
        icon=":material/help:",
    ):
        st.markdown(
            """
            <div style='font-size: 0.85em'>
            A counterfactual explanation helps you explore <strong>“what if” scenarios</strong> — for example, how the patient's risk might change if a clinical parameter were different.
            <br><br>
            This tool reveals which factors <strong>most influence the model’s prediction</strong> and lets you experiment with hypothetical changes.
            <br><br>
            <br>
            <strong>How to read this page:</strong>
            <ul>
                <li>For each feature, you will see:
                    <ul>
                        <li>A <strong>grey field</strong> showing the patient's original value (read-only).</li>
                        <li>An <strong>editable field</strong> where you can change the value to simulate a scenario.</li>
                    </ul>
                </li>
                <li>For numeric features:
                    <ul>
                        <li>A <strong>slider</strong> appears with the value range from real patients in the training data.</li>
                        <li>The slider background uses color shading to guide interpretation:
                            <ul>
                                <li>🔴 <strong>Red</strong> = values linked to higher mortality risk.</li>
                                <li>🔵 <strong>Blue</strong> = values linked to lower mortality risk.</li>
                                <li>🟣 <strong>Purple</strong> = overlapping ranges or uncertain effects.</li>
                            </ul>
                        </li>
                    </ul>
                </li>
            </ul>
            <br>
            <br>
            <strong>How to use this page:</strong>
            <ul>
                <li>Modify one or more feature values to simulate a “what if” scenario.</li>
                <li>Watch how the <strong>predicted risk score updates</strong> in real time.</li>
                <li>Use this tool to explore which changes could lead to a better outcome prediction.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.form("counterfactual_form", clear_on_submit=False):
        dummy_left_col, save_button_col, dummy_right_col = st.columns([
                                                                      1.5, 2, 1.5])
        with save_button_col:
            if st.form_submit_button(
                label="Save Changes before Calculating",
                type="secondary" if st.session_state.counterfactual_data_changed else "primary",
                use_container_width=True,
            ):
                st.session_state.counterfactual_data_changed = True
                st.session_state.counterfactual_changed_state_changed = True

        categorical_feat_col, numeric_feat_col = st.columns([1, 2])
        with categorical_feat_col:
            with st.container(border=True):

                patient_cat_col, scenario_cat_col = st.columns(2)
                with patient_cat_col:
                    ethnicity_options = ("White", "Black", "Hispanic", "Other")
                    patient_ethnicity = st.session_state.patient.get_feature_value(
                        "ethnicity").capitalize()
                    ethnicity_index = ethnicity_options.index(
                        patient_ethnicity) if patient_ethnicity in ethnicity_options else 0
                    ethnicity_pat = st.selectbox(
                        "Ethnicity",
                        ethnicity_options,
                        disabled=True,
                        index=ethnicity_index,
                        key="ethnicity_pat",
                    )

                    gender_options = ("Female", "Male")
                    patient_gender = st.session_state.patient.get_feature_value(
                        "gender").capitalize()
                    gender_index = gender_options.index(
                        patient_gender) if patient_gender in gender_options else 0
                    gender_pat = st.selectbox(
                        "Gender",
                        gender_options,
                        disabled=True,
                        index=gender_index,
                        key="gender_pat",
                    )

                with scenario_cat_col:
                    ethnicity_scenario = st.selectbox(
                        "Ethnicity",
                        ethnicity_options,
                        disabled=False,
                        label_visibility="hidden",
                        index=ethnicity_index,
                        key="ethnicity_scenario",
                    )

                    gender_scenario = st.selectbox(
                        "Gender",
                        gender_options,
                        disabled=False,
                        label_visibility="hidden",
                        index=gender_index,
                        key="gender_scenario",
                    )

                    # Store ethnicity: reset all race options then indicate the selected one
                    for eth in ethnicity_options:
                        st.session_state.counterfactual_patient.demographics[
                            f"race_{eth.lower()}"] = False
                    st.session_state.counterfactual_patient.demographics[
                        f"race_{ethnicity_scenario.lower()}"] = True

                    # Store gender: set keys "gender_F" and "gender_M" appropriately
                    if gender_scenario == "Female":
                        st.session_state.counterfactual_patient.demographics["gender"] = "Female"
                        st.session_state.counterfactual_patient.demographics["gender_F"] = True
                        st.session_state.counterfactual_patient.demographics["gender_M"] = False
                    else:
                        st.session_state.counterfactual_patient.demographics["gender"] = "Male"
                        st.session_state.counterfactual_patient.demographics["gender_F"] = False
                        st.session_state.counterfactual_patient.demographics["gender_M"] = True

            with st.container(border=True):
                # Retrieve the diagnosis dictionary from session state
                diagnosis_dict = st.session_state.patient.diagnosis

                # Get all the keys as options
                diagnosis_options = list(diagnosis_dict.keys())

                # Determine the default options (those with True or 1)
                default_diagnoses = [key for key, value in diagnosis_dict.items() if value in [
                    True, 1]]

                patient_diagnosis = st.multiselect(
                    "Diagnosis",
                    diagnosis_options,
                    default=default_diagnoses,
                    disabled=True,
                    key="diagnosis_pat",
                )

                diagnosis_scenario = st.multiselect(
                    "Diagnosis",
                    diagnosis_options,
                    default=default_diagnoses,
                    disabled=False,
                    key="diagnosis_scenario",
                    label_visibility="collapsed",
                )

                # Update the counterfactual patient dictionary with the selected diagnosis
                updated_diagnosis = {key: (key in diagnosis_scenario)
                                     for key in diagnosis_options}
                st.session_state.counterfactual_patient.update_diagnosis(
                    updated_diagnosis)

            with st.container(border=True):
                # Retrieve the specimen dictionary from session state
                specimen_dict = st.session_state.patient.specimen

                # List all available specimen types
                specimen_options = list(specimen_dict.keys())

                # Determine the default selections (those with True or 1)
                default_specimens = [key for key, value in specimen_dict.items() if value in [
                    True, 1]]

                patient_specimen = st.multiselect(
                    "Specimen",
                    specimen_options,
                    default=default_specimens,
                    disabled=True,
                    key="specimen_pat",
                )

                specimen_scenario = st.multiselect(
                    "Specimen",
                    specimen_options,
                    default=default_specimens,
                    disabled=False,
                    key="specimen_scenario",
                    label_visibility="collapsed",
                )

                # Update the counterfactual patient dictionary with the selected specimen
                updated_specimen = {key: (key in specimen_scenario)
                                    for key in specimen_options}
                st.session_state.counterfactual_patient.update_specimen(
                    updated_specimen)

            with st.container(border=True):
                toggle_features = [
                    "vent",
                    "severe_sepsis_explicit",
                    "positive_culture_poe",
                    "blood_culture_positive",
                    "septic_shock_explicit",
                ]
                patient_toggle_col, scenario_toggle_col = st.columns([3, 1])
                with patient_toggle_col:
                    for feature in toggle_features:
                        default_value = st.session_state.patient.clinical_data.get(
                            feature, False)
                        st.toggle(
                            label=feature.replace("_", " ").capitalize(),
                            value=default_value,
                            disabled=True,
                            key=f"{feature}_pat",
                        )
                with scenario_toggle_col:
                    updated_clinical_data = {}
                    for feature in toggle_features:
                        default_value = st.session_state.patient.clinical_data.get(
                            feature, False)
                        scenario_value = st.toggle(
                            label=feature.replace("_", " ").capitalize(),
                            value=default_value,
                            label_visibility="collapsed",
                            key=f"{feature}_scenario",
                        )
                        updated_clinical_data[feature] = scenario_value

                # Update only the toggle-based keys in counterfactual_patient without affecting numeric keys
                st.session_state.counterfactual_patient.update_clinical_data(
                    updated_clinical_data)

        with numeric_feat_col:
            def build_slider(feature, timeseries=None):
                # Obtain the statistics for the current feature
                raw_stats = st.session_state.patient_base.get_feature_statistics(
                    feature)
                stats = {
                    "min": float(raw_stats["min"]),
                    "max": float(raw_stats["max"]),
                    "survivors_lower": float(raw_stats["survivors_lower"]),
                    "survivors_upper": float(raw_stats["survivors_upper"]),
                    "non_survivors_lower": float(raw_stats["non_survivors_lower"]),
                    "non_survivors_upper": float(raw_stats["non_survivors_upper"]),
                }

                discrete_features = ["sofa", "sirs",
                                     "mingcs", "elixhauser_hospital"]
                if feature in discrete_features:
                    step_size = 1
                else:
                    range_val = stats["max"] - stats["min"]
                    if range_val >= 20:
                        step_size = 1
                    else:
                        step_size = 0.1

                if not timeseries:
                    pat_value = st.session_state.patient.get_feature_value(
                        feature)
                elif timeseries == "vitals":
                    pat_value = st.session_state.patient.get_vital_average(
                        feature)
                elif timeseries == "urineoutput":
                    pat_value = st.session_state.patient.get_urineoutput_average()
                elif timeseries == "vasopressor":
                    pat_value = st.session_state.patient.get_vasopressor_average(
                        feature)

                # Replace underscores with spaces for display purposes
                feature = feature.replace("_", " ")

                return st_counterfactual_slider(
                    key=f"slider_{feature}",
                    name=feature.capitalize(),
                    value=pat_value,
                    min_value=stats["min"],
                    max_value=stats["max"],
                    step=step_size,
                    survivors_lower=stats["survivors_lower"],
                    survivors_upper=stats["survivors_upper"],
                    non_survivors_lower=stats["non_survivors_lower"],
                    non_survivors_upper=stats["non_survivors_upper"],
                )

            # Counterfactual slider for numeric features grouped by categories
            with st.expander("Demographics", expanded=True):
                features = ["age", "weight"]

                for feature in features:
                    # Dynamically assign the slider result to a variable named '<feature>_scenario'
                    globals()[f"{feature}_scenario"] = build_slider(feature)

                # Update the counterfactual patient's demographics with the new age and weight values
                st.session_state.counterfactual_patient.update_demographics({
                    "age": age_scenario,
                    "weight": weight_scenario
                })

            with st.expander("Clinical Features", expanded=True):
                features = [
                    "suspected_infection_time_poe_days",
                    "sofa",
                    "sirs",
                    "mingcs",
                    "elixhauser_hospital"
                ]

                for feature in features:
                    # Dynamically assign the slider result to a variable named '<feature>_scenario'
                    globals()[f"{feature}_scenario"] = build_slider(feature)

                # Save 'suspected_infection_time_poe_days' into clinical_data
                st.session_state.counterfactual_patient.update_clinical_data({
                    "suspected_infection_time_poe_days": suspected_infection_time_poe_days_scenario
                })

                # Save the remaining scores into scores
                st.session_state.counterfactual_patient.update_scores({
                    "sofa": sofa_scenario,
                    "sirs": sirs_scenario,
                    "mingcs": mingcs_scenario,
                    "elixhauser_hospital": elixhauser_hospital_scenario
                })

            with st.expander("Vital Signs", expanded=True):
                features = [
                    "heartrate",
                    "sysbp",
                    "diasbp",
                    "meanbp",
                    "resprate",
                    "tempc",
                    "spo2"
                ]

                for feature in features:
                    slider_value = build_slider(feature, timeseries="vitals")
                    globals()[f"{feature}_scenario"] = slider_value
                    if slider_value is not None:
                        # Update the counterfactual patient's vitals with the new values
                        st.session_state.counterfactual_patient.update_feature_with_scaling(
                            "vitals", feature, slider_value)

            with st.expander("Urine Output", expanded=True):
                urine_scenario = build_slider(
                    "urineoutput", timeseries="urineoutput")
                if urine_scenario is not None:
                    # Update the counterfactual patient's urine output with the new value
                    st.session_state.counterfactual_patient.update_feature_with_scaling(
                        "urineoutput", "urineoutput", urine_scenario)

            with st.expander("Vasopressor", expanded=True):
                features = [
                    "norepinephrine_dose",
                    "epinephrine_dose",
                    "dopamine_dose",
                    "dobutamine_dose",
                    "phenylephrine_dose",
                    "vasopressin_dose"
                ]

                for feature in features:

                    # Dynamically assign the slider result to a variable named '<feature>_scenario'
                    slider_value = build_slider(
                        feature, timeseries="vasopressor")
                    globals()[f"{feature}_scenario"] = slider_value
                    if slider_value is not None:
                        # Update the counterfactual patient's vasopressor with the new values
                        st.session_state.counterfactual_patient.update_feature_with_scaling(
                            "vasopressor", feature, slider_value)

            with st.expander("Laboratory Values", expanded=False):
                # Display an editable laboratory dataframe using st.data_editor.
                laboratory_df = st.session_state.counterfactual_patient.laboratory

                edited_df = st.data_editor(
                    laboratory_df,
                    key="lab_editor",
                    num_rows="dynamic"
                )

                st.session_state.counterfactual_patient.update_laboratory(
                    edited_df
                )

            if st.session_state.get("counterfactual_changed_state_changed"):
                # Reset the flag here to avoid continuously triggering a rerun:
                st.session_state.counterfactual_changed_state_changed = False
                st.rerun()

import os
import csv
import pandas as pd
import streamlit as st
import numpy as np
from .patient_data_model import Patient
from .patient_base import PatientBase
from copy import deepcopy


@st.cache_data
def load_patient_raw_data(file_path, patient_row_index):

    try:
        all_patients = pd.read_csv(
            file_path, sep=",", header=0, encoding="utf-8")

        patient_row = all_patients.iloc[patient_row_index]
        # Round all float values to 2 decimal places; leave ints unchanged
        patient_row = patient_row.apply(
            lambda x: x if pd.isna(x) or isinstance(x, (int, np.integer))
            else round(x, 2) if isinstance(x, (float, np.floating)) else x
        )

        patient = Patient()

        for key in patient.demographics:
            if key in patient_row.index:
                if key == "age":
                    patient.update_demographics(
                        {key: int(patient_row[key]) if pd.notna(patient_row[key]) else None})
                elif key == "weight":
                    patient.update_demographics(
                        {key: float(patient_row[key]) if pd.notna(patient_row[key]) else None})
                else:
                    patient.update_demographics({key: patient_row[key]})

        for key in patient.scores:
            if key in patient_row.index:
                patient.update_scores(
                    {key: float(patient_row[key]) if pd.notna(patient_row[key]) else None})

        for key in patient.clinical_data:
            if key in patient_row.index:
                patient.update_clinical_data({key: patient_row[key]})

        for key in patient.specimen:
            specimen_column = f"specimen_group_{key}"
            if specimen_column in patient_row.index:
                patient.update_specimen(
                    {key: int(patient_row[specimen_column])})

        for key in patient.diagnosis:
            diagnosis_column = f"diagnosis_{key}"
            if diagnosis_column in patient_row.index:
                patient.update_diagnosis(
                    {key: int(patient_row[diagnosis_column])})

        lab_columns = [col.replace("_count", "").replace("_max", "").replace("_min", "").replace("_slope", "").replace("_mean", "")
                       for col in patient_row.index if "_count" in col]

        lab_data = []

        for lab in lab_columns:
            if f"{lab}_count" in patient_row.index:
                lab_data.append({
                    "count": float(patient_row.get(f"{lab}_count", float("nan"))),
                    "mean": round(float(patient_row.get(f"{lab}_mean", float("nan"))), 2),
                    "max": round(float(patient_row.get(f"{lab}_max", float("nan"))), 2),
                    "min": round(float(patient_row.get(f"{lab}_min", float("nan"))), 2),
                    "slope": round(float(patient_row.get(f"{lab}_slope", float("nan"))), 2)
                })

        if lab_data:
            df = pd.DataFrame(lab_data, index=lab_columns).astype("float64")
            patient.update_laboratory(df)

        vitals_data = {}
        for ts in patient.vitals.columns:
            vitals_data[ts] = [float(patient_row[f"{ts}_{i}"]) if f"{ts}_{i}" in patient_row.index and pd.notna(
                patient_row[f"{ts}_{i}"]) else None for i in range(24)]
        patient.update_vitals(vitals_data)

        urineoutput_data = {}
        urineoutput_data["urineoutput"] = [float(patient_row[f"urineoutput_{i}"]) if f"urineoutput_{i}" in patient_row.index and pd.notna(
            patient_row[f"urineoutput_{i}"]) else None for i in range(24)]
        patient.update_urineoutput(pd.DataFrame(urineoutput_data))

        vasopressor_data = {}
        vasopressors = ["dobutamine_dose", "dopamine_dose", "vasopressin_dose",
                        "phenylephrine_dose", "epinephrine_dose", "norepinephrine_dose"]
        for vasopressor in vasopressors:
            vasopressor_data[vasopressor] = [float(patient_row[f"{vasopressor}_{i}"]) if f"{vasopressor}_{i}" in patient_row.index and pd.notna(
                patient_row[f"{vasopressor}_{i}"]) else None for i in range(24)]
        patient.update_vasopressor(pd.DataFrame(vasopressor_data))

        print(f"Loaded patient data for row index {patient_row_index} from {file_path}")
        print(patient.to_dict())
        return patient

    except FileNotFoundError:
        st.error(f"Patient file not found: {file_path}")
        return None


def load_patient_ml_data(file_path, patient_row_index):
    """
    Loads patient ML data from a .npz file.
    Returns a tuple (static, timeseries, y) if y_sel exists, else (static, timeseries, None).
    """
    try:
        data = np.load(file_path, allow_pickle=True)
        static = data['X_static_sel'][patient_row_index]
        timeseries = data['X_timeseries_sel'][patient_row_index]
        y = data['y_sel'][patient_row_index] if 'y_sel' in data else None

        # Formatting for the keras model
        timeseries_data = np.array(timeseries).reshape(
            1, 24, -1).astype(np.float32)
        static_data = np.array(static).reshape(1, -1).astype(np.float32)

        return static_data, timeseries_data, y
    except FileNotFoundError:
        st.error(f"Patient ML file not found: {file_path}")
        return None
    except IndexError:
        st.error(f"Patient index out of range: {patient_row_index}")
        return None


def load_shap_background_data(file_path_ml):
    """
    Loads background static and timeseries data for the SHAP deep explainer.
    Reads all rows from the provided ML file (in .npz format) and extracts the static and timeseries patient data.

    Args:
    file_path_ml (str): Path to the .npz file containing the ML data.

    Returns:
    A tuple (static_data, timeseries_data) where:
        static_data: numpy array with shape [num_patients, num_features] containing the static data,
        timeseries_data: numpy array with shape [num_patients, time_steps, features] containing the timeseries data,
    or (None, None) if loading fails.
    """
    try:
        data = np.load(file_path_ml, allow_pickle=True)
        static_data = data['X_static_sel']
        timeseries_data = data['X_timeseries_sel']
        # Convert data to float32 for the deep explainer
        return static_data.astype(np.float32), timeseries_data.astype(np.float32)
    except FileNotFoundError:
        st.error(f"Patient ML file not found: {file_path_ml}")
        return None, None
    except Exception as e:
        st.error(f"Error loading SHAP background data: {e}")
        return None, None


@st.cache_data
def load_feature_names(file_path):
    # Read only the header of the CSV
    df = pd.read_csv(file_path, sep=",", header=0,
                     index_col=0, encoding="utf-8")
    return list(df.columns)


@st.cache_data
def load_feature_metadata(file_path: str) -> dict:
    """
    Reads a CSV file where the first column contains metadata labels (e.g. "unit",
    "normal_lower", "normal_upper") and returns a dictionary mapping each feature to its metadata.

    Example output:
    {
        'bicarbonate_mean': {
            'unit': 'mEq/L',
            'normal_lower': 22,
            'normal_upper': 26
        },
        ...
    }
    """
    df = pd.read_csv(file_path, header=0, index_col=0, encoding="utf-8")

    feature_metadata = {
        feature: {
            "unit": df.loc["unit", feature],
            "normal_lower": df.loc["normal_lower", feature],
            "normal_upper": df.loc["normal_upper", feature]
        } for feature in df.columns
    }
    return feature_metadata


def load_patient_data(study_xui_selection, current_patient_index):
    """
    Loads patient data based on study selection and patient index.
    """
    print("Loading patient data...")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path_raw = os.path.normpath(os.path.join(
        current_dir, "../data", "patient_raw_data.csv"))
    file_path_ml = os.path.normpath(os.path.join(
        current_dir, "../data", "patient_ml_data.npz"))
    file_path_static_feature_names = os.path.normpath(os.path.join(
        current_dir, "../data", "feature_mapping_static.csv"))
    file_path_timeseries_feature_names = os.path.normpath(os.path.join(
        current_dir, "../data", "feature_mapping_timeseries.csv"))
    file_path_patient_base = os.path.normpath(os.path.join(
        current_dir, "../data", "patient_base_statistics.csv"))
    file_path_global_feature_importance_static = os.path.normpath(os.path.join(
        current_dir, "../data", "global_static_importance.npy"))
    file_path_global_feature_importance_timeseries = os.path.normpath(os.path.join(
        current_dir, "../data", "global_timeseries_importance.npy"))
    if study_xui_selection == 3:  # Training Patient
        patient_row_index = 6
    elif study_xui_selection == 0:  # Explanatory XUI
        if current_patient_index < 3:
            # If patient_order = 0, use 1-3 patients
            if st.session_state.patient_order == 0:
                patient_row_index = current_patient_index
            # If patient_order = 1, use next 4-6 patients
            elif st.session_state.patient_order == 1:
                patient_row_index = current_patient_index + 3
        else:  # Exploratroy XUI
            return None  # All explanatory patients loaded
    else:  # Exploratory
        if current_patient_index < 3:
            if st.session_state.patient_order == 0:
                # Adjust the index for exploratory patients
                exploratory_index = current_patient_index + 3
                patient_row_index = exploratory_index
            elif st.session_state.patient_order == 1:
                patient_row_index = current_patient_index
        else:
            return None  # All exploratory patients loaded

    # Load the patient data
    patient = load_patient_raw_data(file_path_raw, patient_row_index)
    print(f"Loaded patient data for row index {patient_row_index} from {file_path_raw}")
    print(patient.to_dict())
    static, timeseries, y = load_patient_ml_data(
        file_path_ml, patient_row_index)
    patient_ml_data = {"static": static, "timeseries": timeseries, "y": y}
    # Load the feature mapping list
    static_feature_names = load_feature_names(file_path_static_feature_names)
    timeseries_feature_names = load_feature_names(
        file_path_timeseries_feature_names)

    background_static, background_timeseries = load_shap_background_data(
        file_path_ml)

    feature_metadata_static = load_feature_metadata(
        file_path_static_feature_names)
    feature_metadata_timeseries = load_feature_metadata(
        file_path_timeseries_feature_names)
    # Merge the two dictionaries into one.
    # If there are duplicate keys, the timeseries keys will overwrite the static ones.
    combined_feature_metadata = {
        **feature_metadata_static, **feature_metadata_timeseries}
    st.session_state.feature_metadata = combined_feature_metadata

    # Load the patient base statistics
    patient_base = PatientBase()
    patient_base_df = pd.read_csv(
        file_path_patient_base, sep=",", header=0, index_col=0, encoding="utf-8")

    # Convert numeric columns to native Python types to ensure JSON serializability
    for col in patient_base_df.select_dtypes(include=['int64', 'float64']).columns:
        patient_base_df[col] = patient_base_df[col].apply(
            lambda x: int(x) if pd.notnull(x) and isinstance(x, (np.int64, np.int32)) else (
                float(x) if pd.notnull(x) and isinstance(
                    x, (np.float64, np.float32)) else x
            )
        )

    patient_base.set_dataframe(patient_base_df)

    # Save all gathered data into the session state
    st.session_state.patient = patient
    st.session_state.patient.update_ml_data(patient_ml_data)
    st.session_state.static_feature_names = static_feature_names
    st.session_state.timeseries_feature_names = timeseries_feature_names
    st.session_state.background_static = background_static
    st.session_state.background_timeseries = background_timeseries
    st.session_state.patient_base = patient_base

    # Create the counterfactual copy of the patient as initial state
    st.session_state.counterfactual_patient = deepcopy(patient)

    # Load the aggregated SHAP values from the .npy files
    global_static_importance = np.load(
        file_path_global_feature_importance_static)
    global_timeseries_importance = np.load(
        file_path_global_feature_importance_timeseries)

    # Create a DataFrame for the static features using the corresponding session state names.
    df_static = pd.DataFrame({
        "feature": st.session_state.static_feature_names,
        "mean_shap_value": global_static_importance,
        "input_type": "static"
    })

    # Create a DataFrame for the timeseries features using the corresponding session state names.
    df_timeseries = pd.DataFrame({
        "feature": st.session_state.timeseries_feature_names,
        "mean_shap_value": global_timeseries_importance,
        "input_type": "timeseries"
    })

    # Combine the two DataFrames into one
    global_feature_importance_df = pd.concat(
        [df_static, df_timeseries], ignore_index=True)

    # Sort the DataFrame by mean_shap_value in descending order
    global_feature_importance_df = global_feature_importance_df.sort_values(
        by="mean_shap_value", ascending=False)

    # Save the combined and sorted global feature importance DataFrame to session state
    st.session_state.global_feature_importance = global_feature_importance_df

    print("Checking at the end of load_patient_data:")
    print(st.session_state.patient.to_dict())


if __name__ == "__main__":
    load_patient_data(0, 0)
    print(st.session_state.patient.to_dict())
    print(st.session_state.static_feature_names)
    print(st.session_state.timeseries_feature_names)
    print(st.session_state.background_static)
    print(st.session_state.background_timeseries)

    print(st.session_state.patient.get_ml_data())
    print(
        f"Patient age min {st.session_state.patient_base.get_feature_value("age", "min")}")

    print(st.session_state.feature_metadata)

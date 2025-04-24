import streamlit as st
import time
import io
import zipfile
import pandas as pd
import json
import datetime


def generate_single_row_data():
    # Initialize the final flattened dictionary
    final_data = {}

    # 0. Patient Order (0, 1)
    final_data["patient_order"] = st.session_state.get("patient_order")

    # 1. Participant Information (each key directly added)
    participant_info = st.session_state.get("participant_information", {})
    for key, value in participant_info.items():
        final_data[f"participant_{key}"] = value

    # 2. First XUI Evaluated
    final_data["first_xui_evaluated"] = st.session_state.get(
        "first_xui_evaluated")

    # 3. Evaluation - Prediction, Confidence, and Time
    ppt = st.session_state.get("prediction_confidence_time_results", [])

    # Filter the list into two groups based on xui_type.
    # (Not strictly needed now since we use each run’s type, but leaving for clarity.)
    exp_runs = [run for run in ppt if run.get("xui_type") == "explanatory"]
    expl_runs = [run for run in ppt if run.get("xui_type") == "exploratory"]

    # Process explanatory runs using the new key naming.
    for run in exp_runs:
        pid = run.get("patient_index")
        tab = run.get("tab_name")
        # Use prefix "expla" for explanatory.
        key_decision = f"expla_{pid}_{tab}_decision"
        key_confidence = f"expla_{pid}_{tab}_confidence"
        key_time = f"expla_{pid}_{tab}_time"
        final_data[key_decision] = run.get("survival")
        final_data[key_confidence] = run.get("certainty")
        final_data[key_time] = run.get("time_taken")

    # Process exploratory runs using the new key naming.
    for run in expl_runs:
        pid = run.get("patient_index")
        tab = run.get("tab_name")
        # Use prefix "explo" for exploratory.
        key_decision = f"explo_{pid}_{tab}_decision"
        key_confidence = f"explo_{pid}_{tab}_confidence"
        key_time = f"explo_{pid}_{tab}_time"
        final_data[key_decision] = run.get("survival")
        final_data[key_confidence] = run.get("certainty")
        final_data[key_time] = run.get("time_taken")

    # 4. Evaluation - XUI Evaluation Results
    xui_eval = st.session_state.get("xui_evaluation_results", {})
    for key, value in xui_eval.items():
        # Replace key names: if key is numeric (e.g. 0 or 1) then substitute with 'explanatory' or 'exploratory'
        # For simplicity, we assume keys already follow proper naming or are non-numeric.
        final_data[key] = json.dumps(value) if isinstance(
            value, (list, dict)) else value

    # 5. Evaluation - Study Evaluation Results
    study_eval = st.session_state.get("study_evaluation_results", {})
    for key, value in study_eval.items():
        final_data[f"study_{key}"] = json.dumps(
            value) if isinstance(value, (list, dict)) else value

    # 6. Button Orders for each patient (3 columns)
    button_orders = st.session_state.get("button_orders", [])
    for i in range(3):
        order = button_orders[i] if i < len(button_orders) else []
        final_data[f"button_order_patient{i+1}"] = json.dumps(order)

    # 7. Exploratory Dashboard Interactions (group by patient_id)
    interactions_list = st.session_state.get("exploratory_interactions", [])
    grouped_interactions = {}
    for row in interactions_list:
        pid = row.get("patient_id")
        if pid is None:
            continue
        if pid not in grouped_interactions:
            grouped_interactions[pid] = []
        grouped_interactions[pid].append(row)
    for pid, group in grouped_interactions.items():
        final_data[f"exploratory_interactions_patient{pid}"] = json.dumps(
            group)

    # Add a timestamp for when the study was completed
    final_data["study_completed_at"] = str(datetime.datetime.now())
    return final_data


def generate_csv_single_row():
    # Create a CSV output for the single row combined data
    flattened_data = generate_single_row_data()
    df = pd.DataFrame([flattened_data])
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue().encode("utf-8")


def generate_csv_files(participant_prefix):
    files = {}

    # Participant data (as one-row CSV)
    participant_info = st.session_state.get("participant_information", {})
    df_participant = pd.DataFrame([participant_info])
    files[f"{participant_prefix}_participant_data.csv"] = df_participant.to_csv(
        index=False).encode("utf-8")

    # Exploratory interactions (raw)
    interactions = st.session_state.get("exploratory_interactions", [])
    if interactions:
        df_interactions = pd.DataFrame(interactions)
        files[f"{participant_prefix}_interactions.csv"] = df_interactions.to_csv(
            index=False).encode("utf-8")

    # XUI Evaluation Results
    xui_eval = st.session_state.get("xui_evaluation_results", {})
    if xui_eval:
        flat_xui = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                    for k, v in xui_eval.items()}
        df_xui = pd.DataFrame([flat_xui])
        files[f"{participant_prefix}_xui_evaluation.csv"] = df_xui.to_csv(
            index=False).encode("utf-8")

    # Study Evaluation Results
    study_eval = st.session_state.get("study_evaluation_results", {})
    if study_eval:
        flat_study = {f"study_{k}": (json.dumps(v) if isinstance(
            v, (dict, list)) else v) for k, v in study_eval.items()}
        df_study = pd.DataFrame([flat_study])
        files[f"{participant_prefix}_study_evaluation.csv"] = df_study.to_csv(
            index=False).encode("utf-8")

    # Button orders
    button_orders = st.session_state.get("button_orders", [])
    if button_orders:
        data = {}
        for i in range(3):
            order = button_orders[i] if i < len(button_orders) else []
            data[f"patient_{i+1}"] = [json.dumps(order)]
        df_button = pd.DataFrame(data)
        files[f"{participant_prefix}_button_order.csv"] = df_button.to_csv(
            index=False).encode("utf-8")

    # Prediction, Confidence, Time data
    ppt = st.session_state.get("prediction_confidence_time_results", [])
    ppt_flat = {}
    # Instead of listing by run number, use patient_index and tab_name as keys
    for run in ppt:
        pid = run.get("patient_index")
        tab = run.get("tab_name")
        xui_type = run.get("xui_type")
        if xui_type == "explanatory":
            prefix = "expla"
        elif xui_type == "exploratory":
            prefix = "explo"
        else:
            prefix = xui_type
        key_decision = f"{prefix}_{pid}_{tab}_decision"
        key_confidence = f"{prefix}_{pid}_{tab}_confidence"
        key_time = f"{prefix}_{pid}_{tab}_time"
        ppt_flat[key_decision] = run.get("survival")
        ppt_flat[key_confidence] = run.get("certainty")
        ppt_flat[key_time] = run.get("time_taken")
    if ppt_flat:
        df_ppt = pd.DataFrame([ppt_flat])
        files[f"{participant_prefix}_prediction_confidence_time.csv"] = df_ppt.to_csv(
            index=False).encode("utf-8")

    return files


def generate_zip_archive(participant_prefix):
    # Get the combined single row CSV file
    csv_single_row = generate_csv_single_row()

    # Get all individual CSV files as a dictionary: {filename: data}
    csv_files = generate_csv_files(participant_prefix)

    # Create an in-memory ZIP archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add the combined single-row CSV file
        zip_file.writestr(
            f"{participant_prefix}_study_session_data.csv", csv_single_row)

        # Add the separate CSV files
        for filename, data in csv_files.items():
            zip_file.writestr(filename, data)
    zip_buffer.seek(0)
    return zip_buffer


def show_study_completed():
    st.header("Study Completed!")
    st.markdown("""
    ## Thank you for your valuable contribution!
    
    Your responses and interactions have provided essential insights into our AI-based clinical decision support system.
    We greatly appreciate the time and effort you invested in this study.
    
    **What’s next?**
    
    - Your session data has been securely stored and organized.
    - You can download a ZIP archive containing:
      - A combined CSV file with all your session data in one row.
      - Separate CSV files for participant information, interactions, XUI evaluation, study evaluation, button orders, and prediction/confidence/time data.
    
    If you have any questions or feedback regarding the study, please feel free to contact us.
    """)

    st.markdown("Please download your complete session data below:")
    # Get participant number to prefix all filenames.
    participant_info = st.session_state.get("participant_information", {})
    participant_number = participant_info.get("participant_number", "unknown")
    participant_prefix = str(participant_number)

    zip_data = generate_zip_archive(participant_prefix)

    st.markdown("### Download All Data")
    st.download_button(
        label="Download ALL Data as ZIP",
        data=zip_data,
        file_name=f"{participant_prefix}_study_session_data.zip",
        mime="application/zip",
    )
    st.info("Click the button above to download your session data as a ZIP archive.")
    time.sleep(2)

import streamlit as st
import pandas as pd
import io
import zipfile
import time
# Import the needed pages
import subpages.study_start
import subpages.patient_data
import subpages.explanatory_xui
import subpages.exploratory_xui
from subpages.xui_evaluation_form import explanation_satisfaction_form
from subpages.xui_evaluation_form import system_usability_form
from subpages.xui_evaluation_form import nasa_tlx_form
from subpages.xui_evaluation_form import trust_evaluation_form
from subpages.in_between_instruction_screen import show_in_between_instruction
from subpages.study_end_evaluation import study_end_form

if st.session_state.patient_evaluation_running:

    # Show the patient data tab if the patient_data_tab_evaluation_running flag is set
    if st.session_state.patient_data_tab_evaluation_running:
        # Load the patient data page
        subpages.patient_data.display_patient_data()

    # Show the explanatory or exploratory XUI tab based on the flag
    if st.session_state.patient_prediction_tab_evaluation_running:

        # Load the explanatory or exploratory XUI page based on the study selection
        match st.session_state.study_xui_selection:
            case 0:
                subpages.explanatory_xui.display_patient_prediction()
            case 1:
                subpages.exploratory_xui.display_patient_prediction()


elif st.session_state.xui_end_evaluation_running:
    def end_evaluation():
        # Reset the evaluation running flag
        st.session_state.patient_evaluation_running = False
        st.session_state.xui_end_evaluation_running = False
        st.session_state.patient_data_tab_evaluation_running = False
        st.session_state.patient_prediction_tab_evaluation_running = False
        st.session_state.xui_study_running = False

        # Reset the evaluation form flags
        st.session_state.explanation_satisfaction_done = False
        st.session_state.nasa_tlx_done = False
        st.session_state.system_usability_done = False
        st.session_state.trust_evaluation_done = False
        if st.session_state.study_xui_selection == 0:
            st.session_state.explanatory_xui_study_finished = True
        elif st.session_state.study_xui_selection == 1:
            st.session_state.exploratory_xui_study_finished = True
        st.session_state.study_xui_selection = None
        if st.session_state.explanatory_xui_finished_patients == 0 or st.session_state.exploratory_xui_finished_patients == 0:
            st.session_state.current_patient_index = 0

        st.rerun()

    # Flow Control for evaluation forms:
    if not st.session_state.trust_evaluation_done:
        with st.container(border=True):
            trust_evaluation_form()
    elif not st.session_state.explanation_satisfaction_done:
        with st.container(border=True):
            explanation_satisfaction_form()
    elif not st.session_state.nasa_tlx_done:
        with st.container(border=True):
            nasa_tlx_form()
    elif not st.session_state.system_usability_done:
        with st.container(border=True):
            system_usability_form()
    else:
        end_evaluation()

elif st.session_state.end_evaluation_study_running:
    study_end_form()

elif st.session_state.end_evaluation_study_done:
    # ===== Study Finished Message =====
    st.header("Study Completed!")
    st.write(
        """
        ## Thank you for your valuable contribution!
        
        Your responses and interactions have provided us with essential insights. We greatly appreciate your time and effort in helping us improve the AI-based clinical decision support system.
        
        Below you can review your responses and download all the data related to this study session in one click.
        """
    )

    # ===== Display Expanders for Review =====

    with st.expander("Evaluation Results", expanded=False):
        if st.session_state.get("prediction_confidence_time_results"):
            st.markdown("#### Evaluation Results")
            st.write(pd.DataFrame(
                st.session_state.prediction_confidence_time_results))

    with st.expander("Exploratory Interactions", expanded=False):
        if st.session_state.get("exploratory_interactions"):
            st.markdown("#### Interaction Results")
            st.write(pd.DataFrame(st.session_state.exploratory_interactions))
        if st.session_state.get("prediction_confidence_time_results"):
            csv = pd.DataFrame(st.session_state.prediction_confidence_time_results).to_csv(
                index=False).encode('utf-8')
        if st.session_state.get("button_orders"):
            st.markdown("#### Button Orders")
            button_orders_df = pd.DataFrame(st.session_state.button_orders)
            st.write(button_orders_df)

    with st.expander("Participant Information", expanded=False):
        if st.session_state.get("participant_information"):
            st.markdown("#### Participant Information")
            st.write(pd.DataFrame([st.session_state.participant_information]))

    with st.expander("XUI Evaluation Results", expanded=False):
        if st.session_state.get("xui_evaluation_results"):
            st.markdown("#### XUI Evaluation Results")
            df = pd.DataFrame.from_dict(
                st.session_state.xui_evaluation_results, orient="index")
            st.write(df)

    with st.expander("Study Evaluation Results", expanded=False):
        if st.session_state.get("study_evaluation_results"):
            st.markdown("#### Study Evaluation Results")
            st.write(pd.DataFrame([st.session_state.study_evaluation_results]))

    # ===== Download All Data as a ZIP =====

    def generate_zip():
        # Create in-memory files for each session state item we wish to download.
        data_files = {}

        if st.session_state.get("prediction_confidence_time_results"):
            df1 = pd.DataFrame(
                st.session_state.prediction_confidence_time_results)
            data_files["prediction_confidence_time_results.csv"] = df1.to_csv(
                index=False).encode("utf-8")

        if st.session_state.get("exploratory_interactions"):
            df2 = pd.DataFrame(st.session_state.exploratory_interactions)
            data_files["exploratory_interactions.csv"] = df2.to_csv(
                index=False).encode("utf-8")

        if st.session_state.get("button_orders"):
            df3 = pd.DataFrame(st.session_state.button_orders)
            data_files["button_orders.csv"] = df3.to_csv(
                index=False).encode("utf-8")

        if st.session_state.get("participant_information"):
            df4 = pd.DataFrame([st.session_state.participant_information])
            data_files["participant_information.csv"] = df4.to_csv(
                index=False).encode("utf-8")

        if st.session_state.get("xui_evaluation_results"):
            df5 = pd.DataFrame.from_dict(
                st.session_state.xui_evaluation_results, orient="index")
            data_files["xui_evaluation_results.csv"] = df5.to_csv(
                index=False).encode("utf-8")

        if st.session_state.get("study_evaluation_results"):
            df6 = pd.DataFrame([st.session_state.study_evaluation_results])
            data_files["study_evaluation_results.csv"] = df6.to_csv(
                index=False).encode("utf-8")

        # Create an in-memory ZIP file containing all CSV files.
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, data in data_files.items():
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)
        return zip_buffer

    zip_data = generate_zip()

    st.markdown("### Download All Data")
    st.download_button(
        label="Download ALL Data as ZIP",
        data=zip_data,
        file_name="study_session_data.zip",
        mime="application/zip",
    )

    st.info("Click the button above to download all your session data in one file.")

    # Optionally, add a short delay or rerun as needed:
    time.sleep(2)

elif not st.session_state.training_finished:
    subpages.study_start.display_study_start()

else:
    show_in_between_instruction()

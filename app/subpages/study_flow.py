import streamlit as st
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
from subpages.study_data_export import show_study_completed
import streamlit.components.v1 as components

# Check for the scroll flag and trigger scroll if set
if st.session_state.get("trigger_scroll", False):
    time.sleep(0.5)
    components.html(
        """
        <script>
        window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        </script>
        """,
        height=0
    )
    st.toast('Your input has been saved!', icon=':material/task_alt:')
    # Reset the scroll flag so it doesn't run repeatedly
    st.session_state.trigger_scroll = False

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
                subpages.explanatory_xui.display_explanatory_patient_prediction()
            case 1:
                subpages.exploratory_xui.display_exploratory_patient_prediction()


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
    show_study_completed()

elif not st.session_state.training_finished:
    subpages.study_start.display_study_start()

else:
    show_in_between_instruction()

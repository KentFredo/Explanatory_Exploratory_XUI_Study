import streamlit as st
from subpages.participant_details_form import starting_questionnaire
from subpages.informed_consent_form import show_informed_consent_modal
from subpages.training import show_training


def display_study_start():

    if not st.session_state.consent_given:
        show_informed_consent_modal()
        # Check if the starting questionnaire has been completed
    elif not st.session_state.starting_questionnaire_done:
        # Display the starting questionnaire
        starting_questionnaire()
    elif not st.session_state.training_finished:
        show_training()

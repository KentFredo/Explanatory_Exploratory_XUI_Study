import streamlit as st
from subpages.participant_details_form import starting_questionnaire


def display_study_start():

    # Check if the starting questionnaire has been completed
    if not st.session_state.starting_questionnaire_done:
        # Display the starting questionnaire
        starting_questionnaire()
    elif not st.session_state.training_finished:
        st.title("Training for the study")
        st.write(
            "This page offers a training for the study participant to understand the system. ")

        def finish_training():
            st.session_state.training_finished = True

        st.button(
            "Finish Training",
            help="End the training for the study",
            key="finish_training_button",
            on_click=finish_training,
        )

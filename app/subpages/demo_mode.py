import streamlit as st
from subpages.patient_data import display_patient_data
from subpages.explanatory_xui import display_explanatory_patient_prediction
from subpages.exploratory_xui import display_exploratory_patient_prediction

def show_demo_mode():
    # ─────────────────────────────────────────────────────────────────────────────
    #  Render the selected page for the loaded demo patient
    # ─────────────────────────────────────────────────────────────────────────────
    if st.session_state.demo_page == "patient_data":
        display_patient_data()
    elif st.session_state.demo_page == "explanatory":
        display_explanatory_patient_prediction()
    elif st.session_state.demo_page == "exploratory":
        display_exploratory_patient_prediction()

import streamlit as st

st.write(f"Current Study {st.session_state.study_xui_selection}")
st.write(
    f"Number of Finished Patients in Explanatory XUI: {st.session_state.explanatory_xui_finished_patients}")
st.write(
    f"Number of Finished Patients in Exploratory XUI: {st.session_state.exploratory_xui_finished_patients}")

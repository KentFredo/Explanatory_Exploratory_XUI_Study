import streamlit as st


def create_patient_tile():
    """
    Create a patient tile displaying the patient's demographics. Made for a 1 width in a 5.5 overall width.
    """
    demographics = st.session_state.patient.demographics

    if demographics['gender'] == "Male":
        st.markdown("#### John Doe")
    else:
        st.markdown("#### Jane Smith")

    demographic_header_col, demographic_val_col = st.columns(
        2, gap="small")
    with demographic_header_col:
        st.markdown(
            f"""
        <div style="margin-top: -10px; color: #949598; font-size: 0.9rem;">
            <p style="margin-bottom: 0.28rem;">Age:</p>
            <p style="margin-bottom: 0.28rem;">Weight:</p>
            <p style="margin-bottom: 0.23rem;">Ethnicity:</p>
            <p style="margin-bottom: 0.23rem;">Gender:</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with demographic_val_col:
        st.markdown(
            f"""
        <div style="margin-top: -10px;">
            <p style="margin-bottom: 0.1rem;">{demographics['age']} years</p>
            <p style="margin-bottom: 0.1rem;">{demographics['weight']} kg</p>
            <p style="margin-bottom: 0.1rem;">{demographics['ethnicity']}</p>
            <p style="margin-bottom: 0.1rem;">{demographics['gender']}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

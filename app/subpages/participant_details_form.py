import streamlit as st
import streamlit.components.v1 as components
import time
import datetime


def starting_questionnaire():
    # Apply small global text size for questionnaire
    st.markdown("""
        <style>
        .questionnaire-text {
            font-size: 0.9em;
            line-height: 1.5;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("Evaluating an Explainable AI System for Clinical Decision Support")
    st.markdown("""
        <div class="questionnaire-text">
        Thank you for participating in this study. The purpose of this questionnaire is to evaluate your experience 
        with the AI-based clinical decision support system in the form of explanatory and exploratory eXplainable 
        User Interfaces (XUIs). The questionnaire covers different aspects of usability, explainability, trust, and 
        overall satisfaction with the system. There are no right or wrong answers—please respond based on your personal experience. 
        Your responses will help us improve AI-based decision support systems in healthcare. Thank you for your time!
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Meta Data and Demographics")
    with st.form(key="starting_questionnaire_form"):
        # Arrange metadata in 3 columns
        cols_meta = st.columns(3, gap="large")
        with cols_meta[0]:
            participant_number = st.text_input("Participant Number:")
            date = st.date_input("Date:", value=datetime.date.today())
        with cols_meta[1]:
            age = st.number_input("Age:", min_value=0, step=1)
            gender = st.selectbox("Gender:", options=[
                                  "", "Male", "Female", "Other"])
        with cols_meta[2]:
            education_options = [
                "Medical Doctor (MD)", "Nurse", "Medical Student", "Paramedic", "Other"]
            medical_education = st.selectbox(
                "Medical Education:", options=education_options)
            free_text_education = st.text_input(
                "If Education Other, please specify:", value="")
            if medical_education != "Other":
                free_text_education = ""

            primary_specialty = st.text_input("Primary Specialty:")

        st.markdown("---")
        st.subheader("Artificial Intelligence Experience")
        # Arrange knowledge parts in 3 columns
        cols_knowledge = st.columns(3)
        with cols_knowledge[0]:
            ai_knowledge = st.radio("AI Knowledge:", options=[
                                    "Low", "Medium", "High"])
        with cols_knowledge[1]:
            clinical_ai_experience = st.radio(
                "Experience with Clinical AI:", options=["Yes", "No"])
        with cols_knowledge[2]:
            explainable_ai_ui = st.radio(
                "Experience with Explainable AI / UI:", options=["Yes", "No"])

        st.markdown("---")

        st.subheader("Clinical Experience and Experience with Sepsis Patients")
        icu_col, slider_col, years_col = st.columns([1, 1, 1])
        with icu_col:
            icu_experience = st.radio(
                "Have you worked in an ICU?",
                options=["Yes", "No"]
            )
        with slider_col:
            sepsis_experience = st.slider(
                "Rate your experience with sepsis patients:",
                min_value=1,
                max_value=5,
                step=1,
                value=3
            )
            st.markdown(
                "<p style='font-size:0.85em; color:grey; font-style:italic;'>1 = Very Low Experience, 5 = Extensive Experience</p>",
                unsafe_allow_html=True
            )
        with years_col:
            years_clinical = st.slider(
                "Years of Clinical Experience:",
                min_value=0,
                max_value=50,
                step=1,
                value=5
            )

        # Current clinical practice question
        works_clinical = st.radio(
            "Do you currently work in clinical practice?",
            options=["Yes", "No"]
        )

        submit = st.form_submit_button("Submit")
        if submit:
            # Example validation: require participant number and gender
            if not participant_number or not gender:
                st.error(
                    "Please fill out all required fields (e.g., Participant Number, Gender).")
            else:
                starting_data = {
                    "participant_number": participant_number,
                    "date": str(date),
                    "age": age,
                    "gender": gender,
                    "medical_education": medical_education,
                    "other_education": free_text_education,
                    "primary_specialty": primary_specialty,
                    "ai_knowledge": ai_knowledge,
                    "clinical_ai_experience": clinical_ai_experience,
                    "explainable_ai_ui": explainable_ai_ui,
                    "sepsis_experience": sepsis_experience,
                    "worked_icu": icu_experience,
                    "years_clinical": years_clinical,
                    "works_clinical": works_clinical,
                }
                st.session_state.participant_information = starting_data
                st.session_state.starting_questionnaire_done = True
                st.toast('Your input has been saved!',
                         icon=':material/how_to_reg:')
                components.html(
                    "<script>window.parent.scrollTo({ top: 0, behavior: 'smooth' });</script>",
                    height=0
                )
                time.sleep(2)
                st.rerun()

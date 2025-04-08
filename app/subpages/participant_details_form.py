import streamlit as st
import streamlit.components.v1 as components
import time


def starting_questionnaire():
    st.header("Evaluating an Explainable AI System for Clinical Decision Support")
    st.write(
        "Thank you for participating in this study. The purpose of this questionnaire is to evaluate your experience "
        "with the AI-based clinical decision support system in the form of explanatory and exploratory eXplainable "
        "User Interfaces (XUIs). The questionnaire covers different aspects of usability, explainability, trust, and "
        "overall satisfaction with the system. There are no right or wrong answers—please respond based on your personal experience. "
        "Your responses will help us improve AI-based decision support systems in healthcare. Thank you for your time!"
    )

    st.subheader("Meta Data and Demographics")
    with st.form(key="starting_questionnaire_form"):
        # Arrange metadata in 3 columns
        cols_meta = st.columns(3)
        with cols_meta[0]:
            participant_number = st.text_input("Participant Number:")
            date = st.date_input("Date:")
        with cols_meta[1]:
            age = st.number_input("Age:", min_value=0, step=1)
            gender = st.selectbox("Gender:", options=[
                                  "", "Male", "Female", "Other"])
        with cols_meta[2]:
            medical_education = st.text_input("Medical Education:")
            primary_specialty = st.text_input("Primary Specialty:")

        st.markdown("---")
        st.subheader("AI & Clinical Experience")
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

        # Current clinical practice question
        works_clinical = st.radio(
            "Do you currently work in clinical practice?",
            options=["Yes", "No"]
        )

        st.markdown("---")

        st.subheader("Experience with Sepsis Patients")
        slider_col, dummy_col = st.columns([1.5, 1])
        with slider_col:
            # Sepsis experience slider: now 1 to 5 with step 1
            sepsis_experience = st.slider(
                "Rate your experience with sepsis patients:",
                min_value=1,
                max_value=5,
                step=1,
                value=3
            )
            st.markdown(
                "<p style='font-size:0.9em; color:grey; font-style:italic;'>1 = Very Low Experience, 5 = Extensive Experience</p>",
                unsafe_allow_html=True
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
                    "primary_specialty": primary_specialty,
                    "ai_knowledge": ai_knowledge,
                    "clinical_ai_experience": clinical_ai_experience,
                    "explainable_ai_ui": explainable_ai_ui,
                    "sepsis_experience": sepsis_experience,
                    "works_clinical": works_clinical,
                }
                st.session_state.participant_information = starting_data
                st.session_state.starting_questionnaire_done = True

                st.success(
                    "Your responses have been saved for the starting questionnaire!")
                time.sleep(1)
                components.html(
                    """
                    <script>
                      window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                    </script>
                    """,
                    height=0
                )
                st.rerun()

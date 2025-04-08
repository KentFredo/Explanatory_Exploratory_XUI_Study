import streamlit as st
import time


def study_end_form():
    st.header("Study End Questionnaire")
    st.write(
        "Thank you for participating in this study. Please help us improve future studies by answering a few final questions "
        "about your experience with the dashboards."
    )

    with st.form(key="study_end_form"):
        st.subheader("Dashboard Preference")
        dashboard_preference = st.radio(
            "Which dashboard did you prefer?",
            options=["Explanatory", "Exploratory",
                     "I liked them both equally"],
            index=2
        )

        st.subheader("Overall Satisfaction")
        overall_satisfaction = st.slider(
            "Overall, how satisfied were you with the system?",
            min_value=1,
            max_value=5,
            step=1,
            value=3,
            help="1 = Very Unsatisfied, 5 = Very Satisfied"
        )

        st.subheader("Clarity of Explanations")
        clarity_rating = st.slider(
            "How clear were the explanations provided by the system?",
            min_value=1,
            max_value=5,
            step=1,
            value=3,
            help="1 = Not Clear, 5 = Very Clear"
        )

        st.subheader("Usefulness of Dashboard Features")
        useful_features = st.multiselect(
            "Which features of the dashboards did you find most useful? (Select all that apply)",
            options=[
                "Visualization of data",
                "Interactivity",
                "Detailed explanations",
                "Summary metrics",
                "Comparative analysis",
                "Other (please specify below)"
            ]
        )

        st.subheader("Suggestions for Improvement")
        suggestions = st.text_area(
            "Do you have any suggestions for improving the dashboards or overall user interface?",
            placeholder="Type your suggestions here..."
        )

        submit = st.form_submit_button("Submit")
        if submit:
            # Collect responses in a dictionary
            study_end_data = {
                "dashboard_preference": dashboard_preference,
                "overall_satisfaction": overall_satisfaction,
                "clarity_rating": clarity_rating,
                "useful_features": useful_features,
                "suggestions": suggestions,
            }
            st.session_state.study_evaluation_results = study_end_data
            st.session_state.end_evaluation_study_running = False
            st.session_state.end_evaluation_study_done = True
            time.sleep(2)
            st.rerun()

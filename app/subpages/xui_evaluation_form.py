import streamlit as st
import time


def explanation_satisfaction_form():
    st.header("Explanation Satisfaction Scale for Explainable AI")
    st.write(
        "Please rate the following statements based on your experience with the system. "
        "Indicate your level of agreement using the provided scale. There are no right or wrong answers—"
        "choose what best reflects your perception."
    )

    # Display the Likert scale key for users in grey, italic text with 0.9em font size
    st.markdown(
        "<p style='font-size:0.9em; color:grey; font-style:italic;'>Likert Scale: 1 = Strongly Disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree</p>",
        unsafe_allow_html=True
    )

    # Define the questions for Explanation Satisfaction Scale
    questions = {
        1: "From the explanation, I know how the Sepsis Mortality Prediction Model works.",
        2: "This explanation of how the Sepsis Mortality Prediction Model works is satisfying.",
        3: "This explanation of how the Sepsis Mortality Prediction Model works has sufficient detail.",
        4: "This explanation of how the Sepsis Mortality Prediction Model works seems complete.",
        5: "This explanation of how the Sepsis Mortality Prediction Model works tells me how to use it.",
        6: "This explanation of how the Sepsis Mortality Prediction Model works is useful to my goals.",
        7: "This explanation of the Sepsis Mortality Prediction Model shows me how accurate the Model is.",
        8: "This explanation lets me judge when I should trust and not trust the model."
    }

    responses = {}

    # Create a form for the questionnaire
    with st.form(key="explanation_satisfaction_form"):
        # Iterate over each question, using columns for a side-by-side layout.
        for q_number, question_text in questions.items():
            col1, left_label_col, col2, right_label_col = st.columns([
                                                                     3, 0.4, 2, 0.4])
            with col1:
                st.write(f"**{q_number}.** {question_text}")
            with left_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; margin:0;'>Strongly Disagree</p>", unsafe_allow_html=True)
            with col2:
                responses[q_number] = st.radio(
                    label=f"{q_number}",
                    options=[1, 2, 3, 4, 5],
                    index=None,
                    horizontal=True,
                    key=f"explanation_question_{q_number}",
                    label_visibility="collapsed"
                )
            st.markdown(
                "<hr style='margin-top: 0px; margin-bottom: 0px;'>", unsafe_allow_html=True)
            with right_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; text-align:left; margin:0;'>Strongly Agree</p>", unsafe_allow_html=True)

        submit = st.form_submit_button("Submit")
        if submit:
            # Check that all responses have a value
            missing_answers = [
                q for q, resp in responses.items() if resp is None]
            if missing_answers:
                st.error("Please fill out the form completely.")
            else:
                # Save the responses together with study selection info
                evaluation_data = {
                    "study_xui_selection": st.session_state.get("study_xui_selection", None),
                    "responses": responses
                }
                key = f"explan_sat_{st.session_state.get('study_xui_selection', 'default')}"
                st.session_state.xui_evaluation_results[key] = evaluation_data
                st.session_state.explanation_satisfaction_done = True
                # Set a flag to trigger scrolling on the next render
                st.session_state.trigger_scroll = True
                st.rerun()


def system_usability_form():
    st.header("System Usability Scale (SUS)")
    st.write(
        "Please rate the following statements based on your experience with the system. "
        "Indicate your level of agreement using the provided scale. There are no right or wrong answers—"
        "choose what best reflects your perception."
    )

    # Display the Likert scale key for users in grey, italic text with 0.9em font size
    st.markdown(
        "<p style='font-size:0.9em; color:grey; font-style:italic;'>Likert Scale: 1 = Strongly Disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree</p>",
        unsafe_allow_html=True
    )

    # Define the questions for System Usability Scale
    questions = {
        1: "I think that I would like to use this system frequently.",
        2: "I found the system unnecessarily complex.",
        3: "I thought the system was easy to use.",
        4: "I think that I would need the support to be able to use this system.",
        5: "I found the various functions in this system were well integrated.",
        6: "I thought there was too much inconsistency in this system.",
        7: "I would imagine that most people would learn to use this system very quickly.",
        8: "I found the system very cumbersome to use.",
        9: "I felt very confident using the system.",
        10: "I needed to learn a lot of things before I could get going with this system."
    }

    responses = {}

    # Create a form for the System Usability Scale
    with st.form(key="system_usability_form"):
        # Iterate over each question, using columns for a side-by-side layout.
        for q_number, question_text in questions.items():
            col1, left_label_col, col2, right_label_col = st.columns([
                                                                     3, 0.4, 2, 0.4])
            with col1:
                st.write(f"**{q_number}.** {question_text}")
            with left_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; margin:0;'>Strongly Disagree</p>", unsafe_allow_html=True)
            with col2:
                responses[q_number] = st.radio(
                    label=f"{q_number}",
                    options=[1, 2, 3, 4, 5],
                    index=None,
                    horizontal=True,
                    key=f"sus_question_{q_number}",
                    label_visibility="collapsed"
                )
            st.markdown(
                "<hr style='margin-top: 0px; margin-bottom: 0px;'>", unsafe_allow_html=True)
            with right_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; text-align:left; margin:0;'>Strongly Agree</p>", unsafe_allow_html=True)

        submit = st.form_submit_button("Submit")
        if submit:
            # Check that all responses have a value
            missing_answers = [
                q for q, resp in responses.items() if resp is None]
            if missing_answers:
                st.error("Please fill out the form completely.")
            else:
                # Save the responses together with study selection info
                evaluation_data = {
                    "study_xui_selection": st.session_state.get("study_xui_selection", None),
                    "responses": responses
                }
                # Initialize the overall evaluation dictionary if it doesn't exist
                key = f"sus_{st.session_state.get('study_xui_selection', 'default')}"
                st.session_state.xui_evaluation_results[key] = evaluation_data
                st.session_state.system_usability_done = True
                # Set a flag to trigger scrolling on the next render
                st.session_state.trigger_scroll = True
                st.rerun()


def nasa_tlx_form():
    st.header("NASA TLX Score Evaluation")
    st.write(
        "The NASA Task Load Index (NASA-TLX) is designed to assess the workload experienced during a task. "
        "It evaluates different aspects of mental and physical effort, time pressure, perceived success, and emotional strain. "
        "You are asked to reflect on your experience and rate each aspect accordingly. There are no right or wrong answers—please respond based on your personal perception."
    )

    # Define aspects with descriptions, explanations, and explicit left/right labels
    aspects = {
        "Mental Demand": {
            "left_label": "Low cognitive load",
            "right_label": "High cognitive load",
            "explanation": (
                "Evaluates the cognitive processing required during the task, including aspects such as attention, memory, decision-making, and problem solving. "
                "A low rating indicates that the task required little mental effort, while a high rating suggests that it demanded substantial cognitive resources."
            )
        },
        "Physical Demand": {
            "left_label": "Low physical activity",
            "right_label": "High physical activity",
            "explanation": (
                "Measures the degree of physical effort needed to complete the task, such as muscle exertion, manual dexterity, and overall bodily movement. "
                "A low score implies that only minimal physical work was involved, whereas a high score points to significant physical exertion."
            )
        },
        "Temporal Demand": {
            "left_label": "Ample time",
            "right_label": "High time pressure",
            "explanation": (
                "Assesses the time pressure experienced during the task. "
                "A low score indicates that you had sufficient time to complete the task without feeling rushed, while a high score reflects a situation where time was scarce and deadlines were pressing."
            )
        },
        "Performance": {
            "left_label": "Good performance",
            "right_label": "Poor performance",
            "explanation": (
                "Reflects your subjective evaluation of how well you accomplished the task objectives. "
                "A good rating means you believe you performed effectively and met the task requirements, whereas a poor rating suggests that you feel your performance did not meet expectations."
            )
        },
        "Effort": {
            "left_label": "Little effort",
            "right_label": "Intense effort",
            "explanation": (
                "Quantifies the amount of work or exertion you invested to achieve your performance. "
                "A low rating implies the task required minimal effort, while a high rating indicates that you had to work very hard to complete it."
            )
        },
        "Frustration": {
            "left_label": "Calm / unperturbed",
            "right_label": "High frustration / stress",
            "explanation": (
                "Measures the level of stress, irritation, or frustration experienced during the task. "
                "A low score suggests that the task was completed in a calm state, whereas a high score indicates significant emotional discomfort or stress during the process."
            )
        }
    }

    ratings = {}

    with st.form(key="nasa_tlx_form"):
        st.subheader("Rate each Workload Aspect")
        st.write(
            "Use the sliders below to rate each workload aspect. The scale goes from 0 to 100 in increments of 5."
        )

        for aspect, details in aspects.items():
            # Four columns: Aspect name/tooltip, left label, slider, right label
            col_aspect, col_left, col_slider, col_right = st.columns([
                                                                     2, 0.9, 4, 0.9])
            with col_aspect:
                st.markdown(f"**{aspect}**", help=details["explanation"])
            with col_left:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; margin:0;'>{details['left_label']}</p>", unsafe_allow_html=True)
            with col_slider:
                ratings[aspect] = st.slider(
                    label=aspect,
                    min_value=0,
                    max_value=100,
                    step=5,
                    value=0,
                    label_visibility="collapsed",
                    key=f"nasa_{aspect.replace(' ', '_').lower()}"
                )
            with col_right:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; text-align:right; margin:0;'>{details['right_label']}</p>", unsafe_allow_html=True)

        submit = st.form_submit_button("Submit")

    if submit:
        missing = [a for a, r in ratings.items() if r is None]
        if missing:
            st.error("Please fill out all ratings before submitting.")
        else:
            key = f"nasa_tlx_{st.session_state.get('study_xui_selection', 'default')}"
            evaluation_data = {
                "study_xui_selection": st.session_state.get("study_xui_selection", None),
                "ratings": ratings,
            }
            st.session_state.xui_evaluation_results = st.session_state.get(
                "xui_evaluation_results", {})
            st.session_state.xui_evaluation_results[key] = evaluation_data
            st.session_state.nasa_tlx_done = True
            st.session_state.trigger_scroll = True
            st.rerun()


def trust_evaluation_form():
    st.header("Trust Evaluation for Explainable AI")
    st.write(
        "Please rate the following statements based on your experience with the system. "
        "Indicate your level of agreement using the provided scale. There are no right or wrong answers—"
        "choose what best reflects your perception."
    )

    # Display the Likert scale key in grey, italic text with 0.9em font size
    st.markdown(
        "<p style='font-size:0.9em; color:grey; font-style:italic;'>Likert Scale: 1 = Strongly Disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree</p>",
        unsafe_allow_html=True
    )

    # Define the questions for Trust Scale
    questions = {
        1: "I am confident in the Sepsis Mortality Prediction Model. I feel that it works well.",
        2: "The outputs of the Sepsis Mortality Prediction Model are very predictable.",
        3: "The Sepsis Mortality Prediction Model is very reliable. I can count on it to be correct all the time.",
        4: "I feel safe that when I rely on the Sepsis Mortality Prediction Model I will get the right answers.",
        5: "The Sepsis Mortality Prediction Model is efficient in that it works very quickly.",
        6: "I am wary of the Sepsis Mortality Prediction Model.",
        7: "The Sepsis Mortality Prediction Model can perform the task better than a novice human user.",
        8: "I like using the Sepsis Mortality Prediction Model for decision making."
    }

    responses = {}

    # Create a form for the questionnaire
    with st.form(key="trust_scale_form"):
        # Iterate over each question, using columns for a side-by-side layout.
        for q_number, question_text in questions.items():
            col1, left_label_col, col2, right_label_col = st.columns([
                                                                     3, 0.4, 2, 0.4])
            with col1:
                st.write(f"**{q_number}.** {question_text}")
            with left_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; margin:0;'>Strongly Disagree</p>", unsafe_allow_html=True)
            with col2:
                responses[q_number] = st.radio(
                    label=f"{q_number}",
                    options=[1, 2, 3, 4, 5],
                    index=None,
                    horizontal=True,
                    key=f"trust_question_{q_number}",
                    label_visibility="collapsed"
                )
            st.markdown(
                "<hr style='margin-top: 0px; margin-bottom: 0px;'>", unsafe_allow_html=True)
            with right_label_col:
                st.markdown(
                    f"<p style='font-size:0.7em; color:grey; font-style:italic; text-align:left; margin:0;'>Strongly Agree</p>", unsafe_allow_html=True)

        submit = st.form_submit_button("Submit")
        if submit:
            # Check that all responses have a value
            missing_answers = [
                q for q, resp in responses.items() if resp is None]
            if missing_answers:
                st.error("Please fill out the form completely.")
            else:
                # Save the responses together with study selection info
                evaluation_data = {
                    "study_xui_selection": st.session_state.get("study_xui_selection", None),
                    "responses": responses
                }
                key = f"trust_scale_{st.session_state.get('study_xui_selection', 'default')}"
                st.session_state.xui_evaluation_results[key] = evaluation_data
                st.session_state.trust_evaluation_done = True
                # Set a flag to trigger scrolling on the next render
                st.session_state.trigger_scroll = True
                st.rerun()

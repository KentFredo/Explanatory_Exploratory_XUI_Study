import streamlit as st
import time
import streamlit.components.v1 as components


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
            col1, col2 = st.columns([3, 2])  # Adjust the ratio as needed
            with col1:
                st.write(f"**{q_number}.** {question_text}")
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
                st.success(
                    "Your responses have been saved for the Explanation Satisfaction Scale!")
                st.session_state.explanation_satisfaction_done = True
                time.sleep(3)
                components.html(
                    """
                    <script>
                    window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                    </script>
                    """,
                    height=0
                )
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
            col1, col2 = st.columns([3, 2])  # Adjust the ratio as needed
            with col1:
                st.write(f"**{q_number}.** {question_text}")
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
                st.success(
                    "Your responses have been saved for the System Usability Scale (SUS)!")
                time.sleep(3)
                components.html(
                    """
                    <script>
                    window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                    </script>
                    """,
                    height=0
                )
                st.rerun()


def nasa_tlx_form():
    st.header("NASA TLX Score Evaluation")
    st.write(
        "The NASA Task Load Index (NASA-TLX) is designed to assess the workload experienced during a task. "
        "It evaluates different aspects of mental and physical effort, time pressure, perceived success, and emotional strain. "
        "You are asked to reflect on your experience and rate each aspect accordingly. There are no right or wrong answers—please respond based on your personal perception."
    )

    # Define aspects with description and explanation for tooltip
    aspects = {
        "Mental Demand": {
            "desc": "Low = low mental demand, High = high mental demand",
            "explanation": "Measures the mental effort required by the task."
        },
        "Physical Demand": {
            "desc": "Low = low physical demand, High = high physical demand",
            "explanation": "Measures the physical effort required by the task."
        },
        "Temporal Demand": {
            "desc": "Low = low time pressure, High = high time pressure",
            "explanation": "Measures the time pressure felt during the task."
        },
        "Performance": {
            "desc": "Good = good performance, Poor = poor performance",
            "explanation": "Assesses how successful you were in accomplishing the task."
        },
        "Effort": {
            "desc": "Low = low effort, High = high effort",
            "explanation": "Measures how hard you had to work to achieve your performance."
        },
        "Frustration": {
            "desc": "Low = low frustration, High = high frustration",
            "explanation": "Measures your level of stress or frustration during the task."
        }
    }

    pairs = [
        ("Effort", "Performance"),
        ("Temporal Demand", "Frustration"),
        ("Temporal Demand", "Effort"),
        ("Physical Demand", "Frustration"),
        ("Performance", "Frustration"),
        ("Physical Demand", "Temporal Demand"),
        ("Physical Demand", "Performance"),
        ("Temporal Demand", "Mental Demand"),
        ("Frustration", "Effort"),
        ("Performance", "Mental Demand"),
        ("Performance", "Temporal Demand"),
        ("Mental Demand", "Effort"),
        ("Mental Demand", "Physical Demand"),
        ("Effort", "Physical Demand"),
        ("Frustration", "Mental Demand")
    ]

    ratings = {}
    pairwise_selections = {}

    # Wrap all inputs in one form
    with st.form(key="nasa_tlx_form"):
        st.subheader("Rate each Workload Aspect")
        st.write(
            "Use the sliders below to rate each workload aspect. The scale goes from 0 to 100 in increments of 5.")

        for aspect, details in aspects.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                # Display the aspect name with a tooltip question mark
                st.markdown(
                    f"**{aspect}** "
                    f"<span style='display:inline-block; width:16px; height:16px; background-color:grey; color:white; border-radius:50%; text-align:center; line-height:16px; font-size:10px; margin-left:4px;' "
                    f"title='{details['explanation']}'>&#63;</span>",
                    unsafe_allow_html=True,
                )
                # Display the description in grey, italic, 0.7em font size
                st.markdown(
                    f"<p style='color:grey; font-style:italic; font-size:0.7em; margin: 0;'>{details['desc']}</p>",
                    unsafe_allow_html=True,
                )
            with col2:
                ratings[aspect] = st.slider(
                    label=aspect,
                    min_value=0,
                    max_value=100,
                    step=5,
                    value=0,
                    label_visibility="collapsed",
                    key=f"nasa_{aspect.replace(' ', '_').lower()}"
                )

        st.subheader("Pairwise Comparisons")
        st.write(
            "Below, select the factor that had a greater impact on your experience for each pair.")

        # Create a grid layout with 3 pairs per row
        for idx in range(0, len(pairs), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                pair_index = idx + j
                if pair_index < len(pairs):
                    option1, option2 = pairs[pair_index]
                    with col:
                        selection = st.radio(
                            label=f"Pair {pair_index+1}: {option1} vs {option2}",
                            options=[option1, option2],
                            key=f"pairwise_{pair_index+1}",
                            horizontal=False,
                            index=None
                        )
                        pairwise_selections[f"Pair {pair_index+1}"] = selection
        submit = st.form_submit_button("Submit")

    # Process form data after submission (outside the form)
    if submit:
        # Validate that all pairwise comparisons have been answered
        missing_pairs = [
            pair for pair, selection in pairwise_selections.items() if selection is None]
        if missing_pairs:
            st.error("Please fill out the form completely.")
        else:
            evaluation_data = {
                "study_xui_selection": st.session_state.get("study_xui_selection", None),
                "ratings": ratings,
                "pairwise_selections": pairwise_selections,
            }
            key = f"nasa_tlx_{st.session_state.get('study_xui_selection', 'default')}"
            if "xui_evaluation_results" not in st.session_state:
                st.session_state.xui_evaluation_results = {}
            st.session_state.xui_evaluation_results[key] = evaluation_data
            st.session_state.nasa_tlx_done = True
            st.success("Your NASA TLX evaluation has been saved!")
            time.sleep(3)
            components.html(
                """
                <script>
                window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                </script>
                """,
                height=0
            )
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
            col1, col2 = st.columns([3, 2])  # Adjust the ratio as needed
            with col1:
                st.write(f"**{q_number}.** {question_text}")
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
                st.success(
                    "Your responses have been saved for the Trust Scale!")
                st.session_state.trust_evaluation_done = True
                time.sleep(3)
                components.html(
                    """
                    <script>
                    window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                    </script>
                    """,
                    height=0
                )
                st.rerun()

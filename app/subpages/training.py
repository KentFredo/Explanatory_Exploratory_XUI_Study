import streamlit as st
from subpages.patient_data import display_patient_data
from subpages.explanatory_xui import display_explanatory_patient_prediction
from subpages.exploratory_xui import display_exploratory_patient_prediction
import math


def show_training():
    @st.cache_data
    def get_page(string):
        # Display the corresponding page (patient data or prediction displays)
        match string:
            case "display_patient_data":
                display_patient_data()
            case "display_explanatory_patient_prediction":
                display_explanatory_patient_prediction()

    # ----------------------------------------------------------------
    # Disable scrolling completely so the page never moves.
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stMainBlockContainer {
            overflow: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # Reduce the spacing at the top of the page
    st.markdown(
        """
        <style>
        .stMainBlockContainer {
            padding-top: 28px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # Initialize session state variables
    if "current_page" not in st.session_state:
        # Start at 0 (training before patient data)
        st.session_state.current_page = 0
    if "instruction_step" not in st.session_state:
        st.session_state.instruction_step = 0

    # ----------------------------------------------------------------
    # Define training instructions for each page.
    training_instructions = {
        0: [
            {
                "title": "Welcome to the Training",
                "message": "Thank you for participating in this study. This training will guide you through the process and features. Use the buttons at the top to navigate. Click 'Next' to begin.",
                "position": {}
            },
            {
                "title": "Optimizing your Experience",
                "message": "This application is designed for larger screens in landscape mode, as used in clincial practice. Please activate the fullscreen mode with fn+F11 (or Cmd+Shift+F on Mac) for the best experience.",
                "position": {}
            },
            {
                "title": "Navigation Area",
                "message": "This is the navigation area. Use it to move through the study. Your progress is shown with blue icons for pending patients and green for completed ones.",
                "position": {"top": "30%", "left": "40%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "25%", "left": "25%"}
            },
            {
                "title": "Load Patient Data",
                "message": "This button loads patient data, triggers evaluations, or completes UIs. It updates dynamically based on your next task. Please load the data now, then click 'Next'.",
                "position": {"top": "45%", "left": "40%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "25%"}
            },
        ],
        1: [
            {
                "title": "Patient Data Tab",
                "message": "This tab summarizes all clinical data from the first 24 hours after ICU admission, used to predict sepsis mortality risk. Let’s explore it in detail.",
                "position": {}
            },
            {
                "title": "Demographics",
                "message": "This area shows basic patient information such as age and gender.",
                "position": {"top": "40%", "left": "55%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "32%", "left": "36%"}
            },
            {
                "title": "Diagnosis",
                "message": "This section displays grouped patient diagnoses by organ system or function.",
                "position": {"top": "55%", "left": "50%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "30%", "left": "50%"}
            },
            {
                "title": "Scores",
                "message": "Displays scores like SOFA, SIRS, and ELIXHAUSER (highest values), and GCS (lowest value) during ICU stay.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "35%", "left": "67%"}
            },
            {
                "title": "Infection",
                "message": "This section shows suspected infection timing, tests conducted, and results.",
                "position": {"top": "45%", "left": "65%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "30%", "left": "85%"}
            },
            {
                "title": "Laboratory Tests",
                "message": "Shows lab and BGA test results over 24 hours: mean, range, reference values, status, and change over time (slope).",
                "position": {"top": "35%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "55%", "left": "50%"}
            },
            {
                "title": "Trends",
                "message": "Displays hourly trends for vasopressors, vital signs, and urine output. Hover for detailed values. Expand the section if you need a better overview.",
                "position": {"top": "35%", "left": "55%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "50%", "left": "70%"}
            },
            {
                "title": "Patient Data Tab",
                "message": "Take a moment to review the user interface. Feel free to ask questions. Click 'Next' to proceed.",
                "position": {}
            }
        ],
        2: [
            {
                "title": "Explanatory XUI",
                "message": "This is the Explanatory XUI. It shows the predicted mortality risk for the patient we have just seen and a static explanation of key contributing parameters. The prediction model used all data seen on the Patient Data page and explains its decision here.",
                "position": {}
            },
            {
                "title": "Risk Prediction",
                "message": "Shows the predicted mortality risk based on clinical parameters. The color and percentage indicate risk severity.",
                "position": {"top": "45%", "left": "50%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "34%", "left": "50%"}
            },
            {
                "title": "Clinical Interpretation",
                "message": "Provides a brief explanation of the prediction and highlights key contributing features.",
                "position": {"top": "45%", "left": "65%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "30%", "left": "75%"}
            },
            {
                "title": "Risk Evidence",
                "message": "Summarizes features that increased or decreased risk. Their balance strongly influences the prediction.",
                "position": {"top": "50%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "42%", "left": "40%"}
            },
            {
                "title": "Risk Groups",
                "message": "Groups features (e.g. Labs, Vitals) by category. Each group’s total value shows its contribution to the overall risk.",
                "position": {"top": "40%", "left": "65%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "40%"}
            },
            {
                "title": "Textual Explanations",
                "message": "Provides text-based reasoning behind the most influential parameters, comparing to reference ranges, training data and typical  cases.",
                "position": {"top": "35%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "70%"}
            },
            {
                "title": "Explanatory XUI Tab",
                "message": "Review the explanation types on this page, ask questions if anything is unclear, then click 'Next' to continue to the Exploratory XUI.",
                "position": {}
            }
        ],
        3: [
            {
                "title": "Exploratory XUI Tab",
                "message": "This is the Exploratory XUI. It dynamically shows explanations based on your interaction with the system. Decide what information you need to evaluate the patient and the model's prediction.",
                "position": {}
            },
            {
                "title": "Risk Prediction",
                "message": "Shows the patient’s predicted mortality risk. The percentage and color indicate risk severity.",
                "position": {"top": "45%", "left": "50%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "34%", "left": "50%"}
            },
            {
                "title": "Navigation",
                "message": "Use these buttons to explore different explanation tabs. Let’s walk through each one now.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "60%"}
            },
            {
                "title": "Select Risk Explanation",
                "message": "First, we are selecting 'Risk Explanation'.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "60%"}
            },
            {
                "title": "Risk Explanation",
                "message": "This section shows grouped risk explanations similar to those on the previous interface.",
                "position": {"top": "45%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "45%"}
            },
            {
                "title": "Risk Visualization",
                "message": "Displays feature contributions visually. Adjust the number of parameters shown or search manually. Hover over the bars for more info about the values.",
                "position": {"top": "40%", "left": "50%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "65%"}
            },
            {
                "title": "Select Model Behavior",
                "message": "Next, let’s examine the model’s overall top risk factors in the model's behavior.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "60%"}
            },
            {
                "title": "Model Behavior",
                "message": "Shows the most important parameters the model uses to predict sepsis mortality risk on all cases, learned from the training patient set. This gives you an understanding of what parameters the model prioritizes generally.",
                "position": {"top": "40%", "left": "65%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "65%"}
            },
            {
                "title": "Select What-if Analysis",
                "message": "Now, select 'What-if Analysis' to simulate changes in patient data.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "60%"}
            },
            {
                "title": "What-if Analysis",
                "message": "Explore how prediction changes if patient values differ. This helps assess model consistency and sensitivity and lets you explorer how your patient needs to change to get a different risk prediction.",
                "position": {}
            },
            {
                "title": "What-if Analysis",
                "message": "Compare actual and adjusted values. Blue, red, and purple highlight survivor, non-survivor, and overlap zones.",
                "position": {"top": "45%", "left": "70%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "70%", "left": "75%"}
            },
            {
                "title": "What-if Analysis",
                "message": "After adjusting values, click 'Save Changes'.",
                "position": {"top": "40%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "55%", "left": "60%"}
            },
            {
                "title": "What-if Analysis",
                "message": "After saving the scenario values, click 'Calculate Risk' to update the prediction.",
                "position": {"top": "40%", "left": "45%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "30%", "left": "65%"}
            },
            {
                "title": "Select Compare to Typical Cases",
                "message": "Click 'Compare to Typical Cases' to proceed.",
                "position": {"top": "55%", "left": "60%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "45%", "left": "60%"}
            },
            {
                "title": "Compare to Typical Cases",
                "message": "This tab compares patient values with typical survivors, non-survivors and reference ranges. You can adjust which parameter to show.",
                "position": {"top": "45%", "left": "65%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "60%", "left": "65%"}
            },
            {
                "title": "Get further Information",
                "message": "If you are unsure on how to use any of the previously shown pages, just expand this section to get instructions and information on how to use each page.",
                "position": {"top": "35%", "left": "45%", "transform": "translate(-50%, -50%)"},
                "arrow_target": {"top": "50%", "left": "40%"}
            },
            {
                "title": "Exploratory XUI",
                "message": "Choose the tabs you find most helpful. You can revisit, skip, or explore them in any order. Click 'Next' to continue.",
                "position": {}
            }
        ]
    }

    # ----------------------------------------------------------------
    # Define page titles for navigation (for the top nav bar)
    page_titles = {
        0: "Introduction",
        1: "Patient Data",
        2: "Explanatory XUI",
        3: "Exploratory XUI",
        4: "Finish Training",
    }

    # ----------------------------------------------------------------
    # Set the states to open the correct page on the exploratory UI
    if st.session_state.current_page == 3:
        match st.session_state.instruction_step:
            case 0 | 1 | 2 | 3:
                st.session_state.exploratory_view = None
            case 4 | 5:
                st.session_state.exploratory_view = 1
            case 6:
                st.session_state.exploratory_view = None
            case 7:
                st.session_state.exploratory_view = 2
            case 8:
                st.session_state.exploratory_view = None
            case 9 | 10 | 11 | 12:
                st.session_state.exploratory_view = 3
            case 13:
                st.session_state.exploratory_view = None
            case 14 | 15:
                st.session_state.exploratory_view = 4
            case 16:
                st.session_state.exploratory_view = None

    # ----------------------------------------------------------------
    # Top Navigation Bar (acts as both page navigation and training-message navigation)
    with st.container():
        dummy_col_left, col_prev, col_title, col_next, dummy_col_right = st.columns([
                                                                                    1, 1, 2, 1, 1])
        with col_prev:
            if st.button("◀ Previous", use_container_width=True, disabled=(st.session_state.current_page == 0 and (not training_instructions.get(st.session_state.current_page) or st.session_state.instruction_step == 0))):
                if st.session_state.current_page in training_instructions and st.session_state.instruction_step > 0:
                    st.session_state.instruction_step -= 1
                else:
                    if st.session_state.current_page > 0:
                        st.session_state.current_page -= 1
                        if st.session_state.current_page in training_instructions:
                            st.session_state.instruction_step = len(
                                training_instructions[st.session_state.current_page]) - 1
                        else:
                            st.session_state.instruction_step = 0
                st.rerun()
        with col_title:
            title = page_titles.get(
                st.session_state.current_page, f"Page {st.session_state.current_page}"
            )
            if st.session_state.current_page in training_instructions:
                total = len(
                    training_instructions[st.session_state.current_page])
                progress = f" ({st.session_state.instruction_step + 1}/{total})"
            else:
                progress = ""
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: center; height: 50px;">
                    <h3 style="margin: 0; font-size: 24px;">{title}{progress}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_next:
            if st.button("Next ▶", use_container_width=True, disabled=((st.session_state.patient is None and st.session_state.current_page == 0 and st.session_state.instruction_step == 3) or (st.session_state.current_page == (len(page_titles)-1) and (not training_instructions.get(st.session_state.current_page) or st.session_state.instruction_step == (len(training_instructions[st.session_state.current_page]) - 1))))):
                if st.session_state.current_page in training_instructions and st.session_state.instruction_step < len(training_instructions[st.session_state.current_page]) - 1:
                    st.session_state.instruction_step += 1
                    st.rerun()
                    return
                else:
                    st.session_state.current_page += 1
                    st.session_state.instruction_step = 0
                    st.rerun()
        st.markdown(
            "<hr style='border: none; border-top: 1px solid lightgrey; margin: 0px 0px 10px 0px; padding: 0px;' />",
            unsafe_allow_html=True
        )

    # ----------------------------------------------------------------
    # Render the correct training page content based on current_page.
    content_container = st.container()
    with content_container:
        match st.session_state.current_page:
            case 0:
                pass  # For state 0 we may not have any patient data loaded.
            case 1:
                get_page("display_patient_data")
            case 2:
                get_page("display_explanatory_patient_prediction")
            case 3:
                display_exploratory_patient_prediction()
            case 4:
                st.markdown(
                    """

                    <h3 style="text-align: center;">Training Completed</h3>
                    <p style="text-align: center;">You have completed the training and you are now ready to start the study.</p>
                    <p style="text-align: center;">The study team will now tell you what User Interface you will start with.</p>
                    """,
                    unsafe_allow_html=True
                )

                def finish_training():
                    st.session_state.training_finished = True
                    st.session_state.patient_prediction_tab_evaluation_running = False
                    st.session_state.patient_evaluation_running = False
                    st.session_state.patient = None
                    st.session_state.shap_values = None
                    st.session_state.shap_group_contributions = None
                    st.session_state.patient_risk = 0.0
                    st.session_state.scenario_risk = 0.0
                    st.session_state.counterfactual_patient = None
                    st.session_state.counterfactual_data_changed = False
                    st.session_state.current_patient_index = 0
                    st.session_state.exploratory_view = None
                    st.session_state.exploratory_view_start_time = None

                left_empty_col, finish_button_col, right_empty_col = st.columns([
                                                                                2, 1, 2])
                with finish_button_col:
                    st.button(
                        "Finish Training",
                        help="End the training for the study",
                        key="finish_training_button",
                        on_click=finish_training,
                        use_container_width=True,
                        type="primary"

                    )

    # ----------------------------------------------------------------
    # Render the training overlay.
    # For page 0, always show training overlay (no grey background).
    # For pages > 0, only show the overlay if a patient object is loaded.
    overlay_condition = (st.session_state.current_page == 0) or (
        st.session_state.get("patient") is not None)
    if overlay_condition and st.session_state.current_page in training_instructions:
        instructions = training_instructions[st.session_state.current_page]
        if st.session_state.instruction_step < len(instructions):
            current_instruction = instructions[st.session_state.instruction_step]
            modal_title = current_instruction["title"]
            modal_message = current_instruction["message"]

            # Determine modal style based on "position" info (using relative/percentage values).
            pos = current_instruction.get("position", {})
            if not pos:
                pos_style = "top: 50%; left: 60%; transform: translate(-50%, -50%);"
                modal_center_top = 50  # percentage
                modal_center_left = 60
            else:
                pos_style = ""
                modal_center_top = float(pos.get("top", "50%").replace(
                    "%", "")) if "top" in pos else 50
                modal_center_left = float(pos.get("left", "60%").replace(
                    "%", "")) if "left" in pos else 60
                for k, v in pos.items():
                    pos_style += f"{k}: {v};"

            # Build SVG markup for arrow if "arrow_target" is provided.
            arrow_svg = ""
            if "arrow_target" in current_instruction:
                arrow_target = current_instruction["arrow_target"]
                target_top = float(arrow_target.get(
                    "top", "50%").replace("%", ""))
                target_left = float(arrow_target.get(
                    "left", "50%").replace("%", ""))
                x1 = modal_center_left
                y1 = modal_center_top
                x2 = target_left
                y2 = target_top
                arrow_svg = f"""
                <svg style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1000; pointer-events: none;">
                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                          <polygon points="0 0, 10 3.5, 0 7" fill="lightgrey" />
                        </marker>
                    </defs>
                    <line x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%" stroke="lightgrey" stroke-width="2" marker-end="url(#arrowhead)" />
                </svg>
                """

            # Decide whether to use a grey overlay background.
            overlay_div = ""
            if st.session_state.current_page > 0:
                overlay_div = """
                <div class="training-overlay"></div>
                """
            # Render the overlay and modal.
            st.markdown(
                f"""
                <style>
                /* (Only applied if needed) Overlay covering the patient data area below the nav bar */
                .training-overlay {{
                    position: fixed;
                    top: 130px;
                    left: 0;
                    width: 100%;
                    height: calc(100% - 130px);
                    background-color: rgba(255, 255, 255, 0.15);
                    z-index: 997;
                }}
                /* Modal window styling */
                .training-modal {{
                    position: fixed;
                    {pos_style}
                    width: 350px;
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    z-index: 1001;
                    font-family: sans-serif;
                    text-align: center;
                }}
                .training-modal h4 {{
                    margin: 0 0 10px 0;
                    font-size: 1.2rem;
                    color: #444;
                }}
                .training-modal p {{
                    margin: 0;
                    font-size: 1rem;
                    color: #555;
                }}
                </style>
                {overlay_div}
                <div class="training-modal">
                    <h4>{modal_title}</h4>
                    <p>{modal_message}</p>
                </div>
                {arrow_svg}
                """,
                unsafe_allow_html=True
            )

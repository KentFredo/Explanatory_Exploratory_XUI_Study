# Load needed libraries
import streamlit as st      # For streamlit framework
from src.sepsis_mortality_risk_predictor import SepsisMortalityRiskPredictor
import src.data_loader as data_loader
import datetime
import random

# Set the page configuration
st.set_page_config(
    page_title="SepsisVision",
    layout="wide",
    initial_sidebar_state="expanded",  # alternative collapsed
    page_icon="app/assets/logo.png",
)

#####################################################################################
### Set the session_cache                                                         ###
#####################################################################################

# Advanced Coloring for survivors / non-survivors
if "color_survivor" not in st.session_state:
    st.session_state.color_survivor = "#9198e5"
if "color_non_survivor" not in st.session_state:
    st.session_state.color_non_survivor = "#e66465"

# Random seed for button order
if "random_seed" not in st.session_state:
    st.session_state.random_seed = random.randint(1, 10000)

# App mode selection
if "demo_mode_active" not in st.session_state:
    st.session_state.demo_mode_active = False
if "study_mode_active" not in st.session_state:
    st.session_state.study_mode_active = False

# Initialize session state on first run
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False

# Session state for finished training
if 'training_patient_loaded' not in st.session_state:
    st.session_state.training_patient_loaded = False
if "training_finished" not in st.session_state:
    st.session_state.training_finished = False

# Order of patients in the study
# 0: Explanatory: TN, TP, FN; Exploratory: TP, FP, TN
# 1: Explanatory: TP, FP, TN; Exploratory: TN, TP, FN
if "patient_order" not in st.session_state:
    st.session_state.patient_order = 1

# Session state for the prediction model
if "sepsis_prediction_model" not in st.session_state:
    st.session_state.sepsis_prediction_model = SepsisMortalityRiskPredictor()


### Study Flow Session State Variables ###

# Session State for selected Study (0: explanatory, 1: exploratory)
if 'study_xui_selection' not in st.session_state:
    st.session_state.study_xui_selection = None
if 'first_xui_evaluated' not in st.session_state:
    st.session_state.first_xui_evaluated = None

# Session State for selected Patient
if 'current_patient_index' not in st.session_state:
    st.session_state.current_patient_index = 0

# Flags for the XUI Evaluation Flow
if "starting_questionnaire_done" not in st.session_state:
    st.session_state.starting_questionnaire_done = False
if 'participant_information' not in st.session_state:
    st.session_state.participant_information = {}
if "xui_evaluation_results" not in st.session_state:
    st.session_state.xui_evaluation_results = {}
if "study_evaluation_results" not in st.session_state:
    st.session_state.study_evaluation_results = {}
if "explanation_satisfaction_done" not in st.session_state:
    st.session_state.explanation_satisfaction_done = False
if "system_usability_done" not in st.session_state:
    st.session_state.system_usability_done = False
if "nasa_tlx_done" not in st.session_state:
    st.session_state.nasa_tlx_done = False
if "trust_evaluation_done" not in st.session_state:
    st.session_state.trust_evaluation_done = False
if 'trigger_scroll' not in st.session_state:
    st.session_state.trigger_scroll = False


# Session States for the patient evaluation logic:
# Once a new patient is started, the patient_evaluation_running is set to True
# Also the patient_data_tab_evaluation_running is set to True. When the first
# evaluation is done, the patient_data_tab_evaluation_running is set to False
# and the patient_prediction_tab_evaluation_running is set to True.
# When that is finished, the this and the patient_evaluation_running is set to False again.
# When all patients are evaluated, the xui_end_evaluation_running is set to True.

# Session State for the XUI study running
if 'xui_study_running' not in st.session_state:
    st.session_state.xui_study_running = False

# Session State for a currently running patient evaluation
if 'patient_evaluation_running' not in st.session_state:
    st.session_state.patient_evaluation_running = False

# Session state for a currently running patient data tab evaluation
if 'patient_data_tab_evaluation_running' not in st.session_state:
    st.session_state.patient_data_tab_evaluation_running = False

# Session state for a currently running risk prediction evaluation
if 'patient_prediction_tab_evaluation_running' not in st.session_state:
    st.session_state.patient_prediction_tab_evaluation_running = False

if 'xui_end_evaluation_running' not in st.session_state:
    st.session_state.xui_end_evaluation_running = False

if 'end_evaluation_study_running' not in st.session_state:
    st.session_state.end_evaluation_study_running = False
if 'end_evaluation_study_done' not in st.session_state:
    st.session_state.end_evaluation_study_done = False

# Session State for the exploratory view
if 'exploratory_view' not in st.session_state:
    st.session_state.exploratory_view = None
if 'exploratory_view_start_time' not in st.session_state:
    st.session_state.exploratory_view_start_time = None
if "exploratory_interactions" not in st.session_state:
    st.session_state.exploratory_interactions = []
if "button_orders" not in st.session_state:
    st.session_state.button_orders = {}


# Session State for finished patient count
if 'explanatory_xui_finished_patients' not in st.session_state:
    st.session_state.explanatory_xui_finished_patients = 0
if 'exploratory_xui_finished_patients' not in st.session_state:
    st.session_state.exploratory_xui_finished_patients = 0

# Session State for finished XUI studies
if 'explanatory_xui_study_finished' not in st.session_state:
    st.session_state.explanatory_xui_study_finished = False
if 'exploratory_xui_study_finished' not in st.session_state:
    st.session_state.exploratory_xui_study_finished = False

# Session State for the patient data and feature names
if 'patient' not in st.session_state:
    st.session_state.patient = None
if 'counterfactual_patient' not in st.session_state:
    st.session_state.counterfactual_patient = None
if 'counterfactual_data_changed' not in st.session_state:
    st.session_state.counterfactual_data_changed = False
if 'counterfactual_changed_state_changed' not in st.session_state:
    st.session_state.counterfactual_changed_state_changed = False
if 'static_feature_names' not in st.session_state:
    st.session_state.static_feature_names = None
if 'timeseries_feature_names' not in st.session_state:
    st.session_state.timeseries_feature_names = None
if 'feature_metadata' not in st.session_state:
    st.session_state.feature_metadata = None
if 'background_static' not in st.session_state:
    st.session_state.background_static = None
if 'background_timeseries' not in st.session_state:
    st.session_state.background_timeseries = None
if 'patient_base' not in st.session_state:
    st.session_state.patient_base = None
if 'global_feature_importance' not in st.session_state:
    st.session_state.global_feature_importance = None


# Initialize session state variables for participants results
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "show_evaluation_modal" not in st.session_state:
    st.session_state.show_evaluation_modal = False
if "prediction_confidence_time_results" not in st.session_state:
    st.session_state.prediction_confidence_time_results = []


if "patient_risk" not in st.session_state:
    st.session_state.patient_risk = 0.0
if "scenario_risk" not in st.session_state:
    st.session_state.scenario_risk = 0.0

# Initialize SHAP-related variables in session state.
if 'shap_values' not in st.session_state:
    st.session_state.shap_values = None
if 'shap_group_contributions' not in st.session_state:
    st.session_state.shap_group_contributions = None


# Page Layout
# Reduce the spacing at the top of the page
st.markdown(
    """
    <style>
    /* Override the padding of the main content container */
    .stMainBlockContainer {
        padding-top: 45px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Starting the sidebar
with st.sidebar:

    st.markdown(
        """
    <style>
    /* Increase the sidebar width */
    [data-testid="stSidebar"] > div:first-child {
        width: 300px;
    }
    [data-testid="stSidebar"] > div:first-child > div {
        width: 300px;
        /* Adjust the right padding. Modify the padding value as needed. */
        padding-right: 5px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Show the Logo
    st.logo(
        "app/assets/SepsisVision_Logo.png", size="large"
    )

    # Function to load the training patient
    def load_training_patient():
        if not st.session_state.training_patient_loaded:
            data_loader.load_patient_data(3, 0)
            # Calculate the risk for the patient
            print("Checking if patient data is loaded...")
            if st.session_state.patient is None:
                st.write("No patient data loaded. Please check the data loader.")
                return
            risk_array = st.session_state.sepsis_prediction_model.predict_sepsis_mortality_risk()
            st.session_state.patient_risk = round(risk_array[0, 0], 2)

            # Calculate the SHAP values for the patient
            st.session_state.sepsis_prediction_model.generate_local_shap_values()

            # Calculate the mean of timeseries SHAP values for the patient
            st.session_state.sepsis_prediction_model.aggregate_timeseries_shap_values()

            # Now aggregate the SHAP values into overall and category-specific evidence.
            st.session_state.sepsis_prediction_model.aggregate_shap_values()

            # Set a new random seed for the button order
            st.session_state.random_seed = random.randint(1, 10000)

            # Set the training patient loaded flag to True
            st.session_state.training_patient_loaded = True

    def next_study_patient():
        if not st.session_state.patient_evaluation_running and not st.session_state.patient_data_tab_evaluation_running and not st.session_state.patient_prediction_tab_evaluation_running:
            # If the patient evaluation is currently not running, load a new patient and start the new patient study.
            data_loader.load_patient_data(
                st.session_state.study_xui_selection, st.session_state.current_patient_index)

            # Calculate the risk for the patient
            risk_array = st.session_state.sepsis_prediction_model.predict_sepsis_mortality_risk()
            st.session_state.patient_risk = round(risk_array[0, 0], 2)

            # Calculate the SHAP values for the patient
            st.session_state.sepsis_prediction_model.generate_local_shap_values()

            # Calculate the mean of timeseries SHAP values for the patient
            st.session_state.sepsis_prediction_model.aggregate_timeseries_shap_values()

            # Now aggregate the SHAP values into overall and category-specific evidence.
            st.session_state.sepsis_prediction_model.aggregate_shap_values()

            if st.session_state.patient is not None:
                # Start patient evaluation
                st.session_state.xui_study_running = True
                st.session_state.patient_evaluation_running = True
                st.session_state.patient_data_tab_evaluation_running = True

                # Set a new random seed for the button order
                st.session_state.random_seed = random.randint(1, 10000)

                if st.session_state.current_patient_index == 0 and not st.session_state.explanatory_xui_study_finished and not st.session_state.exploratory_xui_study_finished:
                    st.session_state.first_xui_evaluated = st.session_state.study_xui_selection

                # Start the timer.
                st.session_state.start_time = datetime.datetime.now()
            else:
                # No more patients to load.
                st.write("All patients have been evaluated.")

    @st.dialog("Evaluate Patient")
    def evaluate_patient():
        # Record evaluation data
        end_time = datetime.datetime.now()
        time_taken = end_time - st.session_state.start_time

        survival = None
        certainty = None
        button_text = "Submit Evaluation"

        if st.session_state.patient_data_tab_evaluation_running:

            survival = st.radio(
                "Survival", ["Dies", "Survives"], key="survival")
            certainty = st.slider("Certainty (1: Uncertain, 5: Certain)",
                                  min_value=1, max_value=5, step=1, key="certainty")

            button_text = "Submit Evaluation"

        else:
            # Get rating for the patient data tab to load it as default for the slider by loading the last appended element from st.session_state.prediction_confidence_time_results
            last_evaluation = st.session_state.prediction_confidence_time_results[-1]
            last_survival_text = last_evaluation["survival"]
            last_survival = 0 if last_survival_text == "Dies" else 1
            last_certainty = last_evaluation["certainty"]

            survival = st.radio("Survival", ["Dies", "Survives"],
                                key="survival", index=last_survival)
            certainty = st.slider("Certainty (1: Uncertain, 5: Certain)",
                                  min_value=1, max_value=5, step=1, value=last_certainty, key="certainty")

            button_text = "Keep Evaluation" if survival == last_survival_text and certainty == last_certainty else "Update Evaluation"

        if st.button(button_text):
            survival = st.session_state.survival
            certainty = st.session_state.certainty

            # Append data to results list
            st.session_state.prediction_confidence_time_results.append({
                "xui_type": "explanatory" if st.session_state.study_xui_selection == 0 else "exploratory",
                "patient_index": st.session_state.current_patient_index,
                "tab_name": "patient_data" if st.session_state.patient_data_tab_evaluation_running else "prediction_tab",
                "survival": survival,
                "certainty": certainty,
                "time_taken": time_taken.total_seconds(),
            })
            # If the Exploratory Study is running on the exploratory xui, the interaction metric needs to be saved for the last interaction
            if st.session_state.study_xui_selection == 1 and st.session_state.patient_prediction_tab_evaluation_running:
                end_time = datetime.datetime.now()
                time_taken = end_time - st.session_state.exploratory_view_start_time

                st.session_state.exploratory_interactions.append({
                    "patient_id": st.session_state.current_patient_index,
                    "from": st.session_state.exploratory_view,
                    "to": 9,
                    "time_on_from": time_taken.total_seconds(),
                })
                st.session_state.exploratory_view_start_time = None

            # Clear dialog state and patient data
            st.session_state.show_evaluation_dialog = False

            # Logic to move from patient_data_tab to patient_prediction_tab
            if st.session_state.patient_data_tab_evaluation_running:
                st.session_state.patient_data_tab_evaluation_running = False
                st.session_state.patient_prediction_tab_evaluation_running = True
            # Logic to finish a patient evaluation
            elif st.session_state.patient_prediction_tab_evaluation_running:
                st.session_state.patient_prediction_tab_evaluation_running = False
                st.session_state.patient_evaluation_running = False
                st.session_state.patient = None
                st.session_state.shap_values = None
                st.session_state.shap_group_contributions = None
                st.session_state.patient_risk = 0.0
                st.session_state.scenario_risk = 0.0
                st.session_state.counterfactual_patient = None
                st.session_state.counterfactual_data_changed = False
                st.session_state.current_patient_index += 1
                st.session_state.exploratory_view = None

                if st.session_state.study_xui_selection == 0:
                    st.session_state.explanatory_xui_finished_patients += 1
                elif st.session_state.study_xui_selection == 1:
                    st.session_state.exploratory_xui_finished_patients += 1
            st.rerun()

    def evaluate_xui():
        # Logic to evaluate the XUI
        st.session_state.xui_end_evaluation_running = True

    def end_evaluation_study():
        st.session_state.end_evaluation_study_running = True

    if st.session_state.study_mode_active and not st.session_state.demo_mode_active:

        # Determine the defaults for each pill based on the current session state.
        explanatory_default = 0 if st.session_state.study_xui_selection == 0 else None
        exploratory_default = 1 if st.session_state.study_xui_selection == 1 else None

        st.write("XUI Study Selection")
        # Create two columns for the two pill widgets.
        explanatory_pill_col, exploratory_pill_col = st.columns(2)

        with explanatory_pill_col:
            study_explanatory_selection = st.pills(
                label="Explanatory XUI",
                label_visibility='collapsed',
                options=[0],
                format_func=lambda _: "Explanatory XUI",
                selection_mode="single",
                default=explanatory_default,
                disabled=st.session_state.xui_study_running or st.session_state.study_xui_selection == 1 or st.session_state.explanatory_xui_study_finished or not st.session_state.training_finished
            )

        with exploratory_pill_col:
            study_exploratory_selection = st.pills(
                label="Exploratory XUI",
                label_visibility='collapsed',
                options=[1],
                format_func=lambda _: "Exploratory XUI",
                selection_mode="single",
                default=exploratory_default,
                disabled=st.session_state.xui_study_running or st.session_state.study_xui_selection == 0 or st.session_state.exploratory_xui_study_finished or not st.session_state.training_finished
            )

        # Update the shared variable based on which pill is currently active.
        new_selection = None
        if study_explanatory_selection is not None:
            new_selection = 0
        elif study_exploratory_selection is not None:
            new_selection = 1

        # If the selection has changed, update the session state accordingly.
        if new_selection != st.session_state.study_xui_selection:
            st.session_state.study_xui_selection = new_selection
            if new_selection == 0:
                st.session_state.current_patient_index = st.session_state.explanatory_xui_finished_patients
            elif new_selection == 1:
                st.session_state.current_patient_index = st.session_state.exploratory_xui_finished_patients
            st.rerun()

        def build_patient_overview(finished_patients, running_patient=False):
            overview_string = ""
            unfinished = f":blue-badge[:material/personal_injury: "
            finished = f":green-badge[:material/personal_injury: "
            running = f":red-badge[:material/personal_injury: "

            for x in range(1, finished_patients+1):
                overview_string += finished + str(x) + "] "
            for x in range(finished_patients+1, 3+1):
                if running_patient and x == finished_patients + 1:
                    overview_string += running + str(x) + "] "
                else:
                    overview_string += unfinished + str(x) + "] "

            return overview_string.strip()

        pat_overview_col1, pat_overview_col2 = st.columns(2)
        with pat_overview_col1:
            st.write("Finished Patients Explanatory XUI")
            generated_string = build_patient_overview(
                st.session_state.explanatory_xui_finished_patients,
                (st.session_state.patient_evaluation_running and st.session_state.study_xui_selection == 0)
            )
            st.markdown(generated_string)

        with pat_overview_col2:
            st.write("Finished Patients Exploratory XUI")
            generated_string = build_patient_overview(
                st.session_state.exploratory_xui_finished_patients,
                (st.session_state.patient_evaluation_running and st.session_state.study_xui_selection == 1))
            st.markdown(generated_string)

        st.divider()

        st.markdown("## Next Action:")
        # Button logic:
        # This is the main study flow button. It shows either "Load next Patient" or "Evaluate Patient" depending on the state of the patient evaluation.
        if st.session_state.patient_evaluation_running:
            if st.button("Evaluate Patient",
                        type="primary",):
                # Show dialog when button is clicked
                st.session_state.show_evaluation_dialog = True
                evaluate_patient()
        elif not st.session_state.training_patient_loaded:
            st.button(
                "Load Training Patient",
                type="secondary",
                help="Load the training patient",
                key="load_training_patient",
                on_click=load_training_patient,
                disabled=st.session_state.training_patient_loaded is True,
            )
        elif st.session_state.current_patient_index < 3:
            st.button(
                "Load next Patient",
                type="secondary",
                help="Start the next patient study",
                key="load_next_patient",
                on_click=next_study_patient,
                disabled=st.session_state.study_xui_selection is None or st.session_state.current_patient_index >= 3 or not st.session_state.training_finished,
            )
        elif not st.session_state.explanatory_xui_study_finished or not st.session_state.exploratory_xui_study_finished:
            st.button(
                "Evaluate XUI",
                type="secondary",
                help="Evaluate the XUI",
                key="evaluate_xui",
                on_click=evaluate_xui)
        else:
            st.button(
                "Start End Evaluation",
                type="secondary",
                help="Start the end evaluation of this study",
                key="end_evaluation_study",
                on_click=end_evaluation_study,
                disabled=st.session_state.end_evaluation_study_done is True
            )
    elif st.session_state.demo_mode_active and not st.session_state.study_mode_active:
        # ─────────────────────────────────────────────────────────────────────────────
        # Demo‐Mode Sidebar Buttons
        # ─────────────────────────────────────────────────────────────────────────────
        st.write("User Interface Selection")
        
        # Determine which demo‐page is currently selected (default to Patient Data)
        if "demo_page" not in st.session_state:
            st.session_state.demo_page = "patient_data"
    
        if st.button(
            "Patient Data", 
            use_container_width=True, 
            type="secondary" if st.session_state.demo_page != "patient_data" else "primary",
        ):
            st.session_state.demo_page = "patient_data"
            st.rerun()

        if st.button(
            "Explanatory XUI", 
            use_container_width=True, 
            type="secondary" if st.session_state.demo_page != "explanatory" else "primary",
        ):
            st.session_state.demo_page = "explanatory"
            st.rerun()

        if st.button(
            "Exploratory XUI", 
            use_container_width=True, 
            type="secondary" if st.session_state.demo_page != "exploratory" else "primary",
        ):
            st.session_state.demo_page = "exploratory"
            st.rerun()

        st.sidebar.markdown("""---""")

        coldum1, exit_col, coldum2 = st.sidebar.columns([0.5, 2, 0.5])
        with exit_col:
            if st.button(
                "Exit Demo Mode",
                type="secondary",
                help="Exit the demo mode and return to the mode selection page.",
                key="exit_demo_mode",
            ):
                st.session_state.training_patient_loaded = False
                st.session_state.demo_mode_active = False
                st.session_state.study_mode_active = False
                st.session_state.demo_page = None

                st.session_state.patient = None
                st.session_state.shap_values = None
                st.session_state.shap_group_contributions = None
                st.session_state.patient_risk = 0.0
                st.session_state.scenario_risk = 0.0
                st.session_state.counterfactual_patient = None
                st.session_state.counterfactual_data_changed = False
                st.rerun()

    else:
        def set_demo_mode():
            st.session_state.demo_mode_active = True
            st.session_state.study_mode_active = False
            load_training_patient()
        def set_study_mode():
            st.session_state.study_mode_active = True
            st.session_state.demo_mode_active = False
        # If no study mode is active, we show the mode selection page
        st.write("Mode Selection")
        study_mode_col, demo_mode_col = st.columns(2)
        with study_mode_col:
            st.button(
                "Study Mode",
                type="secondary",
                help="Start the study mode",
                key="start_study_mode",
                on_click=set_study_mode,
            )
        with demo_mode_col:
            st.button(
                "Demo Mode",
                type="secondary",
                help="Start the demo mode",
                key="start_demo_mode",
                on_click=set_demo_mode,
            )

#####################################################################################
### Define pages and navigation                                                   ###
#####################################################################################

# Define subpages
study_start_page = st.Page("subpages/study_flow.py",
                           title="Study Flow", default=True)
patient_data_page = st.Page("subpages/patient_data.py",
                            title="Patient Data")
explanatory_xui_page = st.Page("subpages/explanatory_xui.py",
                               title="Explanatory XUI")
exploratory_xui_page = st.Page("subpages/exploratory_xui.py",
                               title="Exploratory XUI")
counterfactual_xui_page = st.Page("subpages/counterfactuals_xui.py",
                                  title="Counterfactual XUI")
information_page = st.Page("subpages/study_information.py",
                           title="Study Information")


# Define the navigation structure
match st.session_state.study_xui_selection:
    case None:
        pg = st.navigation(
            {
                "Study Start Page": [study_start_page],
                "Information": [information_page],
            }, position="hidden"
        )
    case 0:
        pg = st.navigation(
            {
                "Study Start Page": [study_start_page],
                "Patient": [patient_data_page],
                "Explanatory XUI": [explanatory_xui_page],
                "Information": [information_page],
            }, position="hidden"
        )
    case 1:
        pg = st.navigation(
            {
                "Study Start Page": [study_start_page],
                "Patient": [patient_data_page],
                "Exploratory XUI": [exploratory_xui_page, counterfactual_xui_page],
                "Information": [information_page],
            }, position="hidden"
        )
    case _:
        pg = st.navigation(
            {
                "Study Start Page": [study_start_page],
                "Information": [information_page],
            }, position="hidden"
        )

# Run the navigation pages
pg.run()

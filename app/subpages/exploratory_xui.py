import streamlit as st
from components.risk_gauge import create_plotly_risk_gauge
from components.patient_details import create_patient_tile
from subpages.other_patients_comparison import show_other_patients_comparison
from subpages.counterfactuals_xui import show_counterfactual
from subpages.feature_importance_local import show_feature_importance_local
from subpages.feature_importance_global import show_feature_importance_global
import datetime
import random


def display_patient_prediction():
    # Reduce the spacing at the top of the page
    st.markdown(
        """
        <style>
        /* Override the padding of the main content container */
        .stMainBlockContainer {
            padding-top: 60px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Start the counter to also count the interaction without any other exploratory view
    if st.session_state.exploratory_view_start_time is None:
        st.session_state.exploratory_view_start_time = datetime.datetime.now()

    pat_demographics_col, risk_col, transition_col, scenario_risk_col = st.columns([
        1, 1.8, 0.9, 1.8], border=True)

    with pat_demographics_col:
        create_patient_tile()

    with risk_col:
        # Generate the risk score gauge
        patient_risk_fig = create_plotly_risk_gauge(
            st.session_state.patient_risk)
        st.markdown("#### Sepsis Mortality Risk")
        st.plotly_chart(patient_risk_fig, use_container_width=True)

    with transition_col:
        if st.session_state.exploratory_view == 3:
            with st.container():
                # Generate a triangle
                st.markdown(
                    r"""
                    <div style="text-align:center; padding-bottom:20px;">
                        <div style="
                            width: 0px;
                            height: 0px;
                            margin: 0 auto;
                            border-top: 30px solid transparent;
                            border-bottom: 30px solid transparent;
                            border-left: 20px solid #888;">
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Generate the risk calculation button
                if st.button("Calculate Risk", key="calculate_risk_button", type="primary"):
                    st.session_state.counterfactual_patient.convert_to_ml_data()
                    risk_array = st.session_state.sepsis_prediction_model.predict_sepsis_mortality_risk(
                        counterfactual_patient=True)
                    st.session_state.scenario_risk = round(risk_array[0, 0], 2)

                else:
                    pass

    with scenario_risk_col:
        if st.session_state.exploratory_view == 3:
            # Generate the risk score gauge
            scenario_risk_fig = create_plotly_risk_gauge(
                (st.session_state.scenario_risk))
            st.markdown("#### Scenario Risk")
            st.plotly_chart(scenario_risk_fig,
                            use_container_width=True, key="scenario_risk_gauge")
        else:
            pass

    with st.container(border=False):
        def change_exploratory_view(view):
            # Track the change from which exploratory view to which one and how much time spent on the previous view
            end_time = datetime.datetime.now()
            time_taken = end_time - st.session_state.exploratory_view_start_time

            st.session_state.exploratory_interactions.append({
                "patient_id": st.session_state.current_patient_index,
                "from": st.session_state.exploratory_view,
                "to": view,
                "time_on_from": time_taken.total_seconds(),
            })

            # Reset the start time for the new view
            st.session_state.exploratory_view_start_time = datetime.datetime.now()

            # Change the session_state to activate the new view
            st.session_state.exploratory_view = view

        def shuffel_button_positions():

            # Shuffle the button positions
            random.seed(st.session_state.random_seed)
            shuffled_buttons = buttons.copy()
            random.shuffle(shuffled_buttons)
            patient_id = st.session_state.current_patient_index
            st.session_state.button_orders[patient_id] = [
                btn["args"][0] for btn in shuffled_buttons
            ]
            return shuffled_buttons

        buttons = [
            {"label": "Risk Explanation",
                "key": "feature_importance_button", "args": (1,)},
            {"label": "Top Risk Factors",
                "key": "feature_contribution_button", "args": (2,)},
            {"label": "What-if Analysis",
                "key": "counterfactual_button", "args": (3,)},
            {"label": "Compare to Typical Cases",
                "key": "other_patients_button", "args": (4,)},
        ]

        shuffled_buttons = []

        # Check if the current patient index is not in button orders
        if st.session_state.current_patient_index not in st.session_state.button_orders:
            shuffled_buttons = shuffel_button_positions()
        else:
            # Retrieve the shuffled button order for the current patient
            shuffled_buttons = [
                next(btn for btn in buttons if btn["args"][0] == label)
                for label in st.session_state.button_orders[st.session_state.current_patient_index]
            ]

        button1_col, button2_col, button3_col, button4_col = st.columns(4)
        button_cols = [button1_col, button2_col, button3_col, button4_col]

        # Display each button in a shuffled position
        for col, btn in zip(button_cols, shuffled_buttons):
            with col:
                st.button(
                    btn["label"],
                    # ensure unique per seed
                    key=btn["key"] + f"_{st.session_state.random_seed}",
                    on_click=change_exploratory_view,
                    args=btn["args"],
                    use_container_width=True
                )

    with st.container(border=True):
        match st.session_state.exploratory_view:
            case 1:
                show_feature_importance_local()
            case 2:
                show_feature_importance_global()
            case 3:
                show_counterfactual()
            case 4:
                show_other_patients_comparison()
            case _:
                pass

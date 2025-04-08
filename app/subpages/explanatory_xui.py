import streamlit as st
from components.risk_gauge import create_plotly_risk_gauge
from components.patient_details import create_patient_tile
from components.risk_group_table import render_local_group_shap_table, render_local_detail_shap_table
from src.text_explanations_generator import generate_clinical_interpretation
import pandas as pd


def display_patient_prediction():
    # Reduce the spacing at the top of the page
    st.markdown("""
        <style>
        .stMainBlockContainer {
            padding-top: 60px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Top columns layout
    pat_demographics_col, risk_col, interpretation_col = st.columns(
        [1, 1.8, 2.7], border=True)

    with pat_demographics_col:
        create_patient_tile()

    with risk_col:
        fig = create_plotly_risk_gauge(st.session_state.patient_risk)
        st.markdown("#### Sepsis Mortality Risk")
        st.plotly_chart(fig, use_container_width=True)

    with interpretation_col:
        st.markdown("#### Clinical Interpretation")
        clinical_interpretation = generate_clinical_interpretation(
            patient_risk=st.session_state.patient_risk,
            shap_group_contributions=st.session_state.shap_group_contributions
        )
        st.markdown(
            f"<div style='font-size: 0.80em; color: #AAAAAA;'>{clinical_interpretation}</div>",
            unsafe_allow_html=True
        )

    # Replacing st.metrics with an Evidence-Based Summary
    risk_cat_col, risk_detail_col = st.columns(
        [1.5, 3], border=True)

    # Filter out summary categories from the breakdown
    filtered_contributions = {
        k: v for k, v in st.session_state.shap_group_contributions.items()
        if k not in ['Risk ↑ Evidence', 'Risk ↓ Evidence']
    }

    # Sort the contributions once and pass them directly
    sorted_increasing = dict(sorted(
        ((k, v) for k, v in filtered_contributions.items() if v > 0),
        key=lambda x: abs(x[1]),
        reverse=True
    ))

    sorted_decreasing = dict(sorted(
        ((k, v) for k, v in filtered_contributions.items() if v < 0),
        key=lambda x: abs(x[1]),
        reverse=True
    ))

    with risk_cat_col:
        render_local_group_shap_table(
            risk_type="inc",
            shap_dict=sorted_increasing,
        )

        render_local_group_shap_table(
            risk_type="dec",
            shap_dict=sorted_decreasing,
        )

    with risk_detail_col:
        # Detailed SHAP-based explanations
        risk_df = st.session_state.sepsis_prediction_model.create_risk_table().copy()
        render_local_detail_shap_table(
            risk_df, st.session_state.color_non_survivor, st.session_state.color_survivor, top_n=5)

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np


def format_contribution(x):
    """Format contributions with a sign; 0 returns '0.00' and NaN returns 'n/a'."""
    if pd.isnull(x):
        return "n/a"
    elif x == 0:
        return "0.00"
    elif x > 0:
        return f"+{x:.2f}"
    else:
        return f"{x:.2f}"  # Negative values already include the minus sign


def create_parallel_feature_plot():
    patient_base_statistics = st.session_state.patient_base

    # --- Combine SHAP Values from Static and Timeseries ---
    static_feature_names = st.session_state.static_feature_names
    static_shap_list = st.session_state.shap_values['static']
    shap_dict_static = {feature: val for feature,
                        val in zip(static_feature_names, static_shap_list)}
    timeseries_shap = st.session_state.shap_values.get("timeseries_means", {})

    # Merge into one dictionary.
    combined_shap_dict = shap_dict_static.copy()
    combined_shap_dict.update(timeseries_shap)

    # --- Smart Feature Selection based on Combined SHAP values ---
    available_features = patient_base_statistics.get_available_features()
    sorted_features = sorted(available_features, key=lambda f: abs(
        combined_shap_dict.get(f, 0)), reverse=True)
    default_features = sorted_features[:5]

    options = {
        f"{f.replace('_', ' ').title()} ({format_contribution(combined_shap_dict.get(f, 0))})": f
        for f in sorted_features
    }
    selected_feature_options = st.multiselect(
        'Select features for Parallel Coordinates Plot:',
        options=list(options.keys()),
        default=[
            f"{f.replace('_', ' ').title()} ({format_contribution(combined_shap_dict.get(f, 0))})"
            for f in default_features
        ],
        max_selections=10
    )
    selected_features = [options[opt] for opt in selected_feature_options]
    selected_features = sorted(selected_features, key=lambda f: abs(
        combined_shap_dict.get(f, 0)), reverse=True)

    if len(selected_features) < 3:
        st.warning('Please select at least 3 features.')
        st.stop()

    @st.cache_data
    def load_feature_data(selected_features, patient_number=None, xui_selected=None):
        data = {'Feature': [], 'Group': [], 'Value': []}
        for feature in selected_features:
            feature_title = feature.replace("_", " ").title()
            stats = patient_base_statistics.get_feature_statistics(feature)

            # Survivor group (using the average for mean)
            survivor_mean = (stats['survivors_lower'] +
                             stats['survivors_upper']) / 2
            data['Feature'].extend([feature_title] * 3)
            data['Group'].extend(
                ['Survivor', 'Survivor_lower', 'Survivor_upper'])
            data['Value'].extend(
                [survivor_mean, stats['survivors_lower'], stats['survivors_upper']])

            # Non-Survivor group
            nonsurvivor_mean = (
                stats['non_survivors_lower'] + stats['non_survivors_upper']) / 2
            data['Feature'].extend([feature_title] * 3)
            data['Group'].extend(
                ['Non-Survivor', 'Non-Survivor_lower', 'Non-Survivor_upper'])
            data['Value'].extend(
                [nonsurvivor_mean, stats['non_survivors_lower'], stats['non_survivors_upper']])

            # Patient data: can be NaN
            patient_value = st.session_state.patient.get_feature_value(feature)
            data['Feature'].append(feature_title)
            data['Group'].append('Patient')
            data['Value'].append(patient_value)
        return pd.DataFrame(data)

    df_long = load_feature_data(selected_features, st.session_state.current_patient_index,
                                st.session_state.study_xui_selection)

    # --- Improved scaling: Use nan-aware functions, and assign a constant for missing values ---
    scaled_values = []
    selected_features_titles = [
        f.replace("_", " ").title() for f in selected_features]
    # Iterate feature by feature so that each column's scaling is done independently.
    for feature in selected_features_titles:
        feature_vals = df_long.loc[df_long['Feature']
                                   == feature, 'Value'].values
        # Use nanmin and nanmax to ignore missing values in min/max computation.
        min_val = np.nanmin(feature_vals)
        max_val = np.nanmax(feature_vals)
        if max_val == min_val:
            # When all valid values are the same, assign a middle value.
            scaled_feature_vals = [0.5 if not np.isnan(
                val) else 0.5 for val in feature_vals]
        else:
            padding = 0.1 * (max_val - min_val)
            padded_min = min_val - padding
            padded_max = max_val + padding
            # Scale each value and assign 0.5 if the value is missing.
            scaled_feature_vals = [((val - padded_min) / (padded_max - padded_min)) if not np.isnan(val) else 0.5
                                   for val in feature_vals]
        scaled_values.extend(scaled_feature_vals)
    df_long['Scaled Value'] = scaled_values

    # --- Flag missing patient data.
    df_long['IsMissing'] = False
    df_long.loc[(df_long['Group'] == 'Patient') & (
        df_long['Value'].isnull()), 'IsMissing'] = True

    # --- Prepare tooltip data in a separate dataframe ---
    tooltip_data = []
    for feature in selected_features_titles:
        # Get the original feature key (assuming underscores were used in the original key).
        original_feature = feature.replace(" ", "_").lower()
        # Retrieve and clean the unit
        unit = st.session_state.feature_metadata.get(
            original_feature, {}).get("unit", "")
        if pd.isna(unit) or unit in [None, "nan", ""]:
            unit = ""

        # Retrieve reference range values from metadata.
        meta = st.session_state.feature_metadata.get(original_feature, {})
        normal_lower = meta.get("normal_lower", None)
        normal_upper = meta.get("normal_upper", None)
        if (normal_lower not in [None, "", "nan"] and normal_upper not in [None, "", "nan"] and
                not pd.isna(normal_lower) and not pd.isna(normal_upper)):
            reference = f"{normal_lower}-{normal_upper}"
        else:
            reference = ""

        patient_val = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Patient')]['Value'].values[0]
        surv_lower = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Survivor_lower')]['Value'].values[0]
        surv_upper = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Survivor_upper')]['Value'].values[0]
        surv_mean = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Survivor')]['Value'].values[0]
        nonsurv_lower = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Non-Survivor_lower')]['Value'].values[0]
        nonsurv_upper = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Non-Survivor_upper')]['Value'].values[0]
        nonsurv_mean = df_long[(df_long['Feature'] == feature) & (
            df_long['Group'] == 'Non-Survivor')]['Value'].values[0]
        tooltip_data.append({
            'Feature': feature,
            'Unit': unit,
            'Reference': reference,
            'Patient': patient_val,
            'Survivor': f"{surv_lower:.2f} - {surv_upper:.2f} ({surv_mean:.2f})",
            'Non-Survivor': f"{nonsurv_lower:.2f} - {nonsurv_upper:.2f} ({nonsurv_mean:.2f})"
        })
    tooltip_df = pd.DataFrame(tooltip_data)

    # --- Base chart for Patient, Survivor, and Non-Survivor lines and points ---
    base = alt.Chart(
        df_long[df_long['Group'].isin(['Patient', 'Survivor', 'Non-Survivor'])]
    ).encode(
        x=alt.X('Feature:N', sort=selected_features_titles,
                axis=alt.Axis(labelAngle=0, labelAlign='center', title='Feature')),
        y=alt.Y('Scaled Value:Q', axis=None),
        color=alt.Color(
            'Group:N',
            scale=alt.Scale(
                domain=['Survivor', 'Non-Survivor', 'Patient'],
                range=['#A1C9F4', '#FF6961', '#FFC107']
            )
        ),
        detail='Group:N'
    )

    lines = base.mark_line()
    points = base.mark_circle(size=80).encode(
        tooltip=[
            alt.Tooltip('Feature:N', title='Feature'),
            alt.Tooltip('Unit:N', title='Unit'),
            alt.Tooltip('Reference:N', title='Reference'),
            alt.Tooltip('Patient:Q', title='Patient'),
            alt.Tooltip('Survivor:N', title='Survivor'),
            alt.Tooltip('Non-Survivor:N', title='Non-Survivor')
        ]
    ).transform_lookup(
        lookup='Feature',
        from_=alt.LookupData(tooltip_df, 'Feature', [
            'Unit', 'Reference', 'Patient', 'Survivor', 'Non-Survivor'
        ])
    )

    # --- Add layer for missing patient points ---
    missing_patient_data = df_long[(
        df_long['Group'] == 'Patient') & (df_long['IsMissing'])]
    missing_layer = alt.Chart(missing_patient_data).mark_point(
        shape='cross',  # Use a cross marker to indicate missingness
        size=100,
        color='red'
    ).encode(
        x=alt.X('Feature:N', sort=selected_features_titles),
        y=alt.Y('Scaled Value:Q')
    )

    # --- Layers: add a background rule and then all layers.
    layers = []
    rule = alt.Chart(pd.DataFrame({'Feature': selected_features_titles})).mark_rule(color='lightgray').encode(
        x=alt.X('Feature:N', sort=selected_features_titles)
    )
    layers.append(rule)
    layers.append(lines)
    layers.append(points)
    layers.append(missing_layer)

    final_chart = alt.layer(*layers).properties(
        width=700,
        height=400,
        title='Parallel Coordinates Plot'
    ).configure_axis(
        grid=False,
        domain=False
    )
    return final_chart

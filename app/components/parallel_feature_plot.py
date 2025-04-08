import streamlit as st
import pandas as pd
import altair as alt


def create_parallel_feature_plot():
    patient_base_statistics = st.session_state.patient_base

    @st.cache_data
    def load_feature_data(selected_features):
        data = {'Feature': [], 'Group': [], 'Value': []}
        for feature in selected_features:
            stats = patient_base_statistics.get_feature_statistics(feature)

            # Survivor group
            survivor_mean = (stats['survivors_lower'] +
                             stats['survivors_upper']) / 2
            data['Feature'].extend([feature] * 3)
            data['Group'].extend(
                ['Survivor', 'Survivor_lower', 'Survivor_upper'])
            data['Value'].extend(
                [survivor_mean, stats['survivors_lower'], stats['survivors_upper']])

            # Non-Survivor group
            nonsurvivor_mean = (
                stats['non_survivors_lower'] + stats['non_survivors_upper']) / 2
            data['Feature'].extend([feature] * 3)
            data['Group'].extend(
                ['Non-Survivor', 'Non-Survivor_lower', 'Non-Survivor_upper'])
            data['Value'].extend(
                [nonsurvivor_mean, stats['non_survivors_lower'], stats['non_survivors_upper']])

            # Patient data
            patient_value = st.session_state.patient.get_feature_value(feature)
            data['Feature'].append(feature)
            data['Group'].append('Patient')
            data['Value'].append(patient_value)

        return pd.DataFrame(data)

    available_features = patient_base_statistics.get_available_features()
    selected_features = st.multiselect(
        'Select features for Parallel Coordinates Plot:',
        options=available_features,
        default=available_features[:4],
        max_selections=10
    )

    if len(selected_features) < 3:
        st.warning('Please select at least 3 features.')
        st.stop()

    # Load the master dataframe with all data
    df_long = load_feature_data(selected_features)

    # Improved scaling: for each feature, compute padded min and max and then scale values accordingly
    scaled_values = []
    for feature in selected_features:
        feature_vals = df_long.loc[df_long['Feature']
                                   == feature, 'Value'].values
        min_val = feature_vals.min()
        max_val = feature_vals.max()
        # Compute 10% padding on each side
        padding = 0.1 * (max_val - min_val)
        padded_min = min_val - padding
        padded_max = max_val + padding
        # Scale values using the padded range:
        scaled_feature_vals = (feature_vals - padded_min) / \
            (padded_max - padded_min)
        scaled_values.extend(scaled_feature_vals)
    df_long['Scaled Value'] = scaled_values

    # Prepare tooltip data in a separate dataframe
    tooltip_data = []
    for feature in selected_features:
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
            'Patient': patient_val,
            'Survivor': f"{surv_lower:.2f} - {surv_upper:.2f} ({surv_mean:.2f})",
            'Non-Survivor': f"{nonsurv_lower:.2f} - {nonsurv_upper:.2f} ({nonsurv_mean:.2f})"
        })
    tooltip_df = pd.DataFrame(tooltip_data)

    # Base chart for Patient, Survivor, and Non-Survivor lines and points
    base = alt.Chart(df_long[df_long['Group'].isin(['Patient', 'Survivor', 'Non-Survivor'])]).encode(
        x=alt.X('Feature:N', sort=selected_features,
                axis=alt.Axis(labelAngle=0, labelAlign='center')),
        y=alt.Y('Scaled Value:Q', axis=None),
        color=alt.Color(
            'Group:N',
            scale=alt.Scale(
                domain=['Survivor', 'Non-Survivor', 'Patient'],
                range=['#A1C9F4', '#FF6961', '#FFB482']
            )
        ),
        detail='Group:N'
    )
    lines = base.mark_line()
    points = base.mark_circle(size=80).encode(
        tooltip=[
            alt.Tooltip('Feature:N'),
            alt.Tooltip('Patient:Q', title='Patient'),
            alt.Tooltip('Survivor:N', title='Survivor'),
            alt.Tooltip('Non-Survivor:N', title='Non-Survivor')
        ]
    ).transform_lookup(
        lookup='Feature',
        from_=alt.LookupData(tooltip_df, 'Feature', [
                             'Patient', 'Survivor', 'Non-Survivor'])
    )

    # Create a list of layers to be merged using alt.layer
    layers = []

    # Rule layer for feature separation
    rule = alt.Chart(pd.DataFrame({'Feature': selected_features})).mark_rule(color='lightgray').encode(
        x=alt.X('Feature:N', sort=selected_features)
    )
    layers.append(rule)

    # Append lines and points layers for the main data
    layers.append(lines)
    layers.append(points)

    # Combine all layers using alt.layer and return the final chart
    final_chart = alt.layer(*layers).properties(
        width=700,
        height=400,
        title='Parallel Coordinates Plot'
    ).configure_axis(
        grid=False,
        domain=False
    )
    return final_chart

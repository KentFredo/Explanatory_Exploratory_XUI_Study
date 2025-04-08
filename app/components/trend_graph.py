import streamlit as st
import altair as alt
import pandas as pd


def scale_with_margin(series: pd.Series, margin=0.1):
    """
    Return an Altair scale that expands the domain of 'series'
    by ±'margin' (fraction) to avoid points on the extreme edges.
    """
    if series.empty:
        return alt.Scale(domain=[0, 1], nice=False, zero=False)
    min_val = series.min()
    max_val = series.max()
    if min_val == max_val:
        return alt.Scale(domain=[min_val - 1, max_val + 1], nice=False, zero=False)
    span = max_val - min_val
    lower = min_val - span * margin
    upper = max_val + span * margin
    return alt.Scale(domain=[lower, upper], nice=False, zero=False)


def generate_trend_graph():
    # Define a color palette dictionary for the plots.
    color_palette = {
        "vasopressor": ['#FFB347', '#FFCC99', '#FFDAB9', '#FFC0CB', '#FFA07A'],
        "bp_band": '#FF6347',
        "bp_mean": '#F08080',
        "heartrate": '#B0E0E6',
        "resprate": '#5ea9f2',
        "tempc": '#f7e3c1',
        "spo2": '#5ea9f2',
        "urineoutput": '#32CD32'
    }

    # ================================
    # Merge Data into a Single DataFrame
    # ================================

    # Process vitals data.
    vitals_df = st.session_state.patient.vitals.reset_index()

    # Add Urine Output if available.
    if hasattr(st.session_state.patient, "urineoutput") and st.session_state.patient.urineoutput is not None:
        urineoutput_df = st.session_state.patient.urineoutput.copy()
        if not urineoutput_df.empty and "urineoutput" in urineoutput_df.columns:
            vitals_df["urineoutput"] = urineoutput_df["urineoutput"].tolist()

    # Process vasopressor data.
    vaso_df = st.session_state.patient.vasopressor.reset_index()
    vaso_cols = [col for col in vaso_df.columns if col != 'index']
    filtered_vaso_cols = [
        col for col in vaso_cols
        if pd.notnull(vaso_df[col].max()) and vaso_df[col].max() > 0
    ]
    if filtered_vaso_cols:
        # Melt vasopressor data into long format.
        vaso_long_df = vaso_df.melt(
            id_vars=['index'],
            value_vars=filtered_vaso_cols,
            var_name='Medication',
            value_name='Dose'
        )
    else:
        vaso_long_df = pd.DataFrame(
            columns=['index', 'Medication', 'Dose'])

    # Merge vitals and vasopressor data on "index" (outer join).
    trend_df = pd.merge(vitals_df, vaso_long_df, on='index', how='outer')

    trend_df['BP'] = (
        trend_df['sysbp'].astype(int).astype(str) + '/' +
        trend_df['diasbp'].astype(int).astype(str) +
        " (" + trend_df['meanbp'].astype(int).astype(str) + ")"
    )

    # ================================
    # Define the Unified Tooltip and Selection
    # ================================
    tooltip_cols = [
        alt.Tooltip('index:Q', title='Time'),
        alt.Tooltip('Medication:N', title='Medication'),
        alt.Tooltip('Dose:Q', title='Dose'),
        alt.Tooltip('BP:N', title='BP'),
        alt.Tooltip('heartrate:Q', title='Heart Rate'),
        alt.Tooltip('resprate:Q', title='Resp Rate'),
        alt.Tooltip('spo2:Q', title='SpO2'),
        alt.Tooltip('tempc:Q', title='Temp (°C)'),
        alt.Tooltip('urineoutput:Q', title='Urine Output')
    ]

    nearest = alt.selection_point(
        fields=['index'], nearest=True, on='mouseover', empty='none', name='shared'
    )

    # Create a unified selector layer based on trend_df.
    selector = alt.Chart(trend_df).mark_point(opacity=0.01).encode(
        x='index:Q',
        tooltip=tooltip_cols
    ).add_params(nearest)

    # ================================
    # Vasopressor Chart
    # ================================
    if filtered_vaso_cols:
        # Note: We still use the original vaso_df for transforming the vasopressor data.
        folded = alt.Chart(vaso_df).transform_fold(
            filtered_vaso_cols,
            as_=['Medication', 'Dose']
        )

        vaso_line = folded.mark_line().encode(
            x=alt.X('index:Q', axis=alt.Axis(
                title=None, labels=False, ticks=False)),
            y=alt.Y('Dose:Q', title='Vasopressor',
                    scale=alt.Scale(zero=False, nice=True),
                    axis=alt.Axis(titleAngle=-90, titlePadding=0, titleAlign="center", titleX=-55, format=".1f")),
            color=alt.Color(
                'Medication:N',
                scale=alt.Scale(range=color_palette["vasopressor"]),
                legend=alt.Legend(orient='top', title=None)
            ),
            tooltip=tooltip_cols
        ).properties(
            width=700,
            height=90
        )

        vaso_rule = alt.Chart(vaso_df).mark_rule(color='gray').encode(
            x='index:Q'
        ).transform_filter(nearest)

        vaso_selector = folded.mark_point(opacity=0.01).encode(
            x='index:Q',
            tooltip=tooltip_cols
        ).add_params(nearest)

        vaso_chart = (vaso_line + vaso_rule + vaso_selector)
    else:
        empty_df = pd.DataFrame({'index': range(24), 'dummy': [0]*24})
        vaso_chart = alt.Chart(empty_df).mark_line(opacity=0).encode(
            x=alt.X('index:Q', axis=alt.Axis(
                title=None, labels=False, ticks=False)),
            y=alt.Y('dummy:Q', title='Vasopressor',
                    axis=alt.Axis(titleAngle=-90, titlePadding=0, titleAlign="center", titleX=-55, format=".1f"))
        ).properties(
            height=90,
            width=700,
        )

    # ================================
    # Vitals / Circulation Charts
    # ================================
    st.markdown("#### Trends")
    # Filter trend_df for rows with vitals data
    vitals_for_plot = trend_df[trend_df['diasbp'].notnull()].copy()

    bp_min = min(vitals_for_plot["diasbp"].min(),
                 vitals_for_plot["sysbp"].min(), vitals_for_plot["meanbp"].min())
    bp_max = max(vitals_for_plot["diasbp"].max(),
                 vitals_for_plot["sysbp"].max(), vitals_for_plot["meanbp"].max())
    bp_span = bp_max - bp_min
    margin_val = 0.1  # 10% margin
    bp_lower = bp_min - bp_span * margin_val
    bp_upper = bp_max + bp_span * margin_val
    bp_scale = alt.Scale(
        domain=[bp_lower, bp_upper], nice=True, zero=False)

    bp_band = alt.Chart(vitals_for_plot).mark_area(
        opacity=0.15,
        color=color_palette["bp_band"]
    ).encode(
        x=alt.X('index:Q',
                axis=alt.Axis(title=None, labels=False, ticks=False, domain=False)),
        y=alt.Y('diasbp:Q',
                title='Circulation',
                scale=bp_scale,
                axis=alt.Axis(format="0f", titleAngle=-90, titlePadding=0, titleAlign="center", titleX=-55)),
        y2='sysbp:Q',
        tooltip=tooltip_cols
    )

    bp_mean = alt.Chart(vitals_for_plot).mark_line(
        color=color_palette["bp_mean"],
        strokeWidth=1
    ).encode(
        x=alt.X('index:Q',
                axis=alt.Axis(title=None, labels=False, ticks=False, domain=False)),
        y=alt.Y('meanbp:Q', scale=bp_scale),
        tooltip=tooltip_cols
    )

    hr_line = alt.Chart(vitals_for_plot).mark_line(
        color=color_palette["heartrate"]
    ).encode(
        x=alt.X('index:Q',
                axis=alt.Axis(title=None, labels=False, ticks=False, domain=False)),
        y=alt.Y('heartrate:Q', scale=bp_scale),
        tooltip=tooltip_cols
    )

    bp_rule = alt.Chart(vitals_for_plot).mark_rule(color='gray').encode(
        x='index:Q'
    ).transform_filter(nearest)

    bp_chart = (bp_band + bp_mean + hr_line + bp_rule + selector).properties(
        height=90,
        width=700,
    )

    # ================================
    # Other Vital Signs Charts
    # ================================
    vitals_color_map = {
        "resprate": color_palette["resprate"],
        "tempc": color_palette["tempc"],
        "spo2": color_palette["spo2"]
    }

    desired_order = ['spo2', 'resprate', 'tempc', 'urineoutput']
    other_cols = [col for col in desired_order if col in trend_df.columns]
    other_charts = []
    for i, col in enumerate(other_cols):
        show_x = (i == len(other_cols) - 1)
        chart_rule = alt.Chart(trend_df).mark_rule(color='gray').encode(
            x='index:Q'
        ).transform_filter(nearest)
        line_color = vitals_color_map.get(col, '#ADD8E6')
        chart = alt.Chart(trend_df).mark_line(color=line_color).encode(
            x=alt.X('index:Q', axis=alt.Axis(
                title="Time" if show_x else None,
                labels=show_x, ticks=show_x, domain=show_x
            )),
            y=alt.Y(f'{col}:Q',
                    title=col.title(),
                    scale=scale_with_margin(trend_df[col], margin=0.1),
                    axis=alt.Axis(format="0f", titlePadding=0, titleAlign="center", titleX=-55)),
            tooltip=tooltip_cols
        ).properties(height=90, width=700)
        combined_chart = (chart + chart_rule + selector)
        other_charts.append(combined_chart)

    # ================================
    # Concatenate the Charts Vertically
    # ================================
    all_charts = alt.vconcat(
        vaso_chart,
        bp_chart,
        *other_charts,
        spacing=3
    ).configure_view(stroke=None)

    return all_charts

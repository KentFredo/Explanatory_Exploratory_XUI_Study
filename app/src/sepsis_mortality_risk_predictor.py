import tensorflow as tf
import streamlit as st
import numpy as np
import pandas as pd
import os
import shap
import random
from data.feature_category_mapping import FEATURE_CATEGORY_MAPPING, TIMESERIES_FEATURE_MAPPING
import pickle


class SepsisMortalityRiskPredictor:
    @st.cache_resource
    def load_prediction_model(_self):
        """Loads a Keras neural network model from a .keras file."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.normpath(os.path.join(
            current_dir, "../models", "sepsis_mortality_model.keras"))
        model = tf.keras.models.load_model(model_path)
        return model

    @st.cache_resource
    def load_scalers(_self):
        """Loads the scaler objects for static and timeseries data."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        static_scaler_path = os.path.normpath(os.path.join(
            current_dir, "../models", "scaler_static.pkl"))
        timeseries_scaler_path = os.path.normpath(os.path.join(
            current_dir, "../models", "scaler_timeseries.pkl"))
        with open(static_scaler_path, "rb") as f:
            static_scaler = pickle.load(f)
        with open(timeseries_scaler_path, "rb") as f:
            timeseries_scaler = pickle.load(f)

        return static_scaler, timeseries_scaler

    def __init__(self):
        # Load the pre-trained keras tensorflow model and scaler objects using the method via self.
        self.model = self.load_prediction_model()
        self.static_scaler, self.timeseries_scaler = self.load_scalers()

    def predict_sepsis_mortality_risk(self, counterfactual_patient=False) -> np.ndarray:
        # Extract timeseries and static components from the raw patient data
        if not counterfactual_patient:
            # Use the original patient data
            patient_ml_data = st.session_state.patient.get_ml_data()
        else:
            # Use the counterfactual patient data
            patient_ml_data = st.session_state.counterfactual_patient.get_ml_data()

        # Extract timeseries and static data
        timeseries_data = patient_ml_data.get('timeseries')
        static_data = patient_ml_data.get('static')

        # Predict sepsis mortality risk using the two input streams
        predictions = self.model.predict([static_data, timeseries_data])
        return predictions

    def generate_local_shap_values(self):
        """
        Generate local SHAP values for the current patient's data using the loaded Keras model.
        The SHAP values are computed using the GradientExplainer, which is suitable for deep learning models.
        The SHAP values are stored in the session state for later use.
        Note: The SHAP values are multiplied by 100 to present them as percentages.
        Returns:
            None: The SHAP values are stored in the session state.
        """

        # Retrieve patient raw data
        patient_ml_data = st.session_state.patient.get_ml_data()
        timeseries_data = patient_ml_data.get('timeseries')
        static_data = patient_ml_data.get('static')

        # For background data, here we reuse the same sample.
        # For improved explanations, consider using a larger background dataset.
        background_static = st.session_state.background_static
        background_timeseries = st.session_state.background_timeseries

        # Initialize SHAP GradientExplainer using the model and background data.
        explainer = shap.GradientExplainer(
            self.model, [background_static, background_timeseries]
        )

        # Compute the SHAP values for the current patient's data.
        shap_values = explainer.shap_values([static_data, timeseries_data])

        # Split shap values into static and timeseries.
        shap_static = np.array(shap_values[0])
        # Bring static SHAP values into the right format: reshape to 1D array and multiply by 100.
        shap_static = shap_static.flatten() * 100

        # Multiply timeseries SHAP values by 100 as well, if you wish to express them in percentage points.
        shap_timeseries = shap_values[1] * 100

        st.session_state.shap_values = {
            "static": shap_static,
            "timeseries": shap_timeseries
        }

    def aggregate_timeseries_shap_values(self):
        # Define the vital feature names in the same order as in the timeseries data.
        vital_features = st.session_state.timeseries_feature_names
        # Retrieve the timeseries SHAP values from session state.
        timeseries_shap = st.session_state.shap_values['timeseries']

        # Remove any singleton dimensions (if the array has shape like (T, 1, N, 1), for example).
        # The squeezed version should have shape (num_timesteps, num_features).
        timeseries_shap_squeezed = np.squeeze(timeseries_shap)

        # Sum over the time axis (axis 0) so that each feature's contribution is aggregated.
        # This results in an array with one value per feature.
        aggregated_shap = np.round(timeseries_shap_squeezed.sum(axis=0), 1)

        # Create a dictionary mapping the vital feature names to their aggregated SHAP value.
        aggregated_shap_dict = {feature: value for feature,
                                value in zip(vital_features, aggregated_shap)}

        # Save the aggregated results into session state under the key 'timeseries_means'
        st.session_state.shap_values['timeseries_means'] = aggregated_shap_dict

    def aggregate_shap_values(self):
        """
        Aggregates static and timeseries SHAP values into overall positive/negative evidence
        and by feature category.

        Returns:
            None: The function saves aggregated contributions to st.session_state.shap_group_contributions.
        """
        import numpy as np
        # --- Static Features Aggregation ---
        # Load the static SHAP values from session state.
        static_values = st.session_state.shap_values["static"]

        # --- Timeseries Features Aggregation ---
        # Retrieve the aggregated timeseries SHAP values as a dictionary
        # (for example: {"heartrate": value, "sysbp": value, ...}).
        timeseries_aggregated = st.session_state.shap_values.get(
            "timeseries_means", {})

        # Calculate the overall evidence for static values.
        static_positive = np.nansum(static_values[static_values > 0])
        static_negative = np.nansum(static_values[static_values < 0])

        # Calculate the overall evidence for timeseries values.
        # Use a list comprehension to extract only the values; missing keys default to 0.
        timeseries_positive = np.nansum(
            [v for v in timeseries_aggregated.values() if v > 0])
        timeseries_negative = np.nansum(
            [v for v in timeseries_aggregated.values() if v < 0])

        # Now combine both static and timeseries evidence.
        positive_evidence = int(static_positive + timeseries_positive)
        negative_evidence = int(static_negative + timeseries_negative)

        shap_group_contributions = {
            "Risk ↑ Evidence": positive_evidence,
            "Risk ↓ Evidence": negative_evidence
        }

        # Aggregate static contributions per category, based on your previous mapping.
        for category, indices in FEATURE_CATEGORY_MAPPING.items():
            valid_indices = [i for i in indices if i < len(static_values)]
            category_sum = int(np.nansum(static_values[valid_indices]))
            shap_group_contributions[category] = category_sum

        # For timeseries features, aggregate contributions per category using explicit feature names.
        for category, features in TIMESERIES_FEATURE_MAPPING.items():
            category_sum = int(
                np.nansum([timeseries_aggregated.get(feat, 0) for feat in features]))
            shap_group_contributions[category] = category_sum

        # Save the complete mapping to session state.
        st.session_state.shap_group_contributions = shap_group_contributions

    def create_risk_table(_self, shorten_table=True):
        """
        Combines raw patient data with both static and timeseries (aggregated) SHAP values
        into a risk table with enhanced descriptions.
        """

        def format_value_with_unit(feature, raw_value):
            """
            Format a raw feature value by appending its unit (if available)
            from st.session_state.feature_metadata.
            """
            if pd.isna(raw_value):
                return ""

            unit = st.session_state.feature_metadata.get(
                feature.lower(), {}).get("unit", "")
            if unit == "" or unit is None or pd.isna(unit) or str(unit).lower() == "nan":
                unit = None

            if isinstance(raw_value, (int, float)):
                formatted = f"{raw_value:.2f}"
            else:
                formatted = str(raw_value)

            return f"{formatted} {unit}" if unit else formatted

        # Get the required data from session state.
        static_shap_values = st.session_state.shap_values['static']
        static_feature_names = st.session_state.static_feature_names
        patient_base = st.session_state.patient_base

        # Prepare rows for static features.
        rows = []
        for i in range(len(static_shap_values)):
            feature_name = static_feature_names[i]
            raw_value = st.session_state.patient.get_feature_value(
                feature_name)
            formatted_value = format_value_with_unit(feature_name, raw_value)
            risk_contribution = static_shap_values[i]

            abs_contrib = abs(risk_contribution)
            if abs_contrib > 5:
                contribution_strength = "much"
            elif abs_contrib > 3:
                contribution_strength = "slightly"
            else:
                contribution_strength = "not much"

            description_parts = [
                f"The parameter '{feature_name.replace('_', ' ').title()}' contributes {contribution_strength} to the risk."
            ]
            comparison_parts = []

            try:
                # NEW: Add reference range comparison as the first sentence.
                if raw_value is not None:
                    meta = st.session_state.feature_metadata.get(
                        feature_name.lower(), {})
                    normal_lower = meta.get("normal_lower", None)
                    normal_upper = meta.get("normal_upper", None)
                    # Only add the sentence if both bounds exist.
                    # Check that both bounds are provided and not NaN or empty.
                    if (normal_lower not in [None, ""] and normal_upper not in [None, ""] and
                            not pd.isna(normal_lower) and not pd.isna(normal_upper)):
                        try:
                            normal_lower = float(normal_lower)
                            normal_upper = float(normal_upper)
                            if raw_value < normal_lower:
                                range_sentence = f"Compared to the reference range ({normal_lower}-{normal_upper}), the patient's value is LOW."
                            elif raw_value > normal_upper:
                                range_sentence = f"Compared to the reference range ({normal_lower}-{normal_upper}), the patient's value is HIGH."
                            else:
                                range_sentence = f"The patient's value is in the normal reference range ({normal_lower}-{normal_upper})."
                            comparison_parts.insert(0, range_sentence)
                        except Exception:
                            pass

                feature_stats = patient_base.get_feature_statistics(
                    feature_name)
                if raw_value is not None:
                    min_val = feature_stats['min']
                    max_val = feature_stats['max']
                    survivors_lower = feature_stats['survivors_lower']
                    survivors_upper = feature_stats['survivors_upper']
                    non_survivors_lower = feature_stats['non_survivors_lower']
                    non_survivors_upper = feature_stats['non_survivors_upper']

                    comparison_text = "Compared to the patient training base of spesis-3 ICU patients, this value is "
                    relative_position = []
                    if raw_value < (min_val + (max_val - min_val) * 0.1):
                        relative_position.append("comparatively low")
                    elif raw_value > (max_val - (max_val - min_val) * 0.1):
                        relative_position.append("comparatively high")
                    if relative_position:
                        comparison_text += f"{' and '.join(relative_position)}."
                        comparison_parts.append(comparison_text)

                    in_survivor_range = survivors_lower <= raw_value <= survivors_upper
                    in_non_survivor_range = non_survivors_lower <= raw_value <= non_survivors_upper
                    range_info = []
                    if in_survivor_range and in_non_survivor_range:
                        range_info.append(
                            "in the overlapping range of survivors and non-survivors")
                    elif in_survivor_range:
                        range_info.append(
                            "within the typical range of survivors")
                    elif in_non_survivor_range:
                        range_info.append(
                            "within the typical range of non-survivors")

                    if range_info:
                        comparison_parts.append(
                            f"Here, the patient's value is {', '.join(range_info)}.")
                    else:
                        comparison_parts.append(
                            "The patient's value is outside the typical range of both survivors and non-survivors.")
                else:
                    comparison_parts.append(
                        "The patient's value is not available.")
            except ValueError as e:
                comparison_parts.append(
                    f"Statistics not available for this feature: {e}")

            row = {
                "Parameter": feature_name,
                "Raw Value": formatted_value,
                "Risk Contribution": risk_contribution,
                "Description": " ".join(description_parts),
                "Comparison": " ".join(comparison_parts)
            }
            rows.append(row)

        # Process the aggregated timeseries SHAP values.
        timeseries_aggregated = st.session_state.shap_values.get(
            "timeseries_means", {})

        for feature, shap_value in timeseries_aggregated.items():
            raw_value = st.session_state.patient.get_feature_value(feature)
            formatted_value = format_value_with_unit(feature, raw_value)
            abs_contrib = abs(shap_value)
            if abs_contrib > 5:
                contribution_strength = "much"
            elif abs_contrib > 3:
                contribution_strength = "slightly"
            else:
                contribution_strength = "not much"

            description_parts = [
                f"Over the observed time period, the parameter '{feature.replace('_', ' ').title()}' contributes {contribution_strength} to the risk."
            ]
            comparison_parts = []

            try:
                # NEW: Add reference range sentence for the aggregated value.
                if raw_value is not None:
                    meta = st.session_state.feature_metadata.get(
                        feature.lower(), {})
                    normal_lower = meta.get("normal_lower", None)
                    normal_upper = meta.get("normal_upper", None)
                    if (normal_lower not in [None, ""] and normal_upper not in [None, ""] and
                            not pd.isna(normal_lower) and not pd.isna(normal_upper)):
                        try:
                            normal_lower = float(normal_lower)
                            normal_upper = float(normal_upper)
                            if raw_value < normal_lower:
                                range_sentence = f"Compared to the reference range ({normal_lower}-{normal_upper}), the patient's value is LOW."
                            elif raw_value > normal_upper:
                                range_sentence = f"Compared to the reference range ({normal_lower}-{normal_upper}), the patient's value is HIGH."
                            else:
                                range_sentence = f"The patient's value is in the normal reference range ({normal_lower}-{normal_upper})."
                            comparison_parts.insert(0, range_sentence)
                        except Exception:
                            pass

                feature_stats = patient_base.get_feature_statistics(feature)
                if raw_value is not None:
                    min_val = feature_stats['min']
                    max_val = feature_stats['max']
                    survivors_lower = feature_stats['survivors_lower']
                    survivors_upper = feature_stats['survivors_upper']
                    non_survivors_lower = feature_stats['non_survivors_lower']
                    non_survivors_upper = feature_stats['non_survivors_upper']

                    comparison_text = "Compared to the patient base, this aggregated value is "
                    relative_position = []
                    if raw_value < (min_val + (max_val - min_val) * 0.1):
                        relative_position.append("comparatively low")
                    elif raw_value > (max_val - (max_val - min_val) * 0.1):
                        relative_position.append("comparatively high")
                    if relative_position:
                        comparison_text += f"{' and '.join(relative_position)}."
                        comparison_parts.append(comparison_text)

                    in_survivor_range = survivors_lower <= raw_value <= survivors_upper
                    in_non_survivor_range = non_survivors_lower <= raw_value <= non_survivors_upper
                    range_info = []
                    if in_survivor_range and in_non_survivor_range:
                        range_info.append(
                            "in the overlapping range of survivors and non-survivors")
                    elif in_survivor_range:
                        range_info.append(
                            "within the typical range of survivors")
                    elif in_non_survivor_range:
                        range_info.append(
                            "within the typical range of non-survivors")

                    if range_info:
                        comparison_parts.append(
                            f"The patient's aggregated value is {', '.join(range_info)}.")
                    else:
                        comparison_parts.append(
                            "The patient's aggregated value is outside the typical range of both survivors and non-survivors.")
                else:
                    comparison_parts.append(
                        "The patient's value is not available.")
            except ValueError as e:
                comparison_parts.append(
                    f"Statistics not available for this feature: {e}")

            row = {
                "Parameter": feature,
                "Raw Value": formatted_value,
                "Risk Contribution": shap_value,
                "Description": " ".join(description_parts),
                "Comparison": " ".join(comparison_parts)
            }
            rows.append(row)

        # Build the DataFrame.
        df = pd.DataFrame(rows)
        df["Absolute Risk Contribution"] = df["Risk Contribution"].abs()
        df = df.sort_values(by="Absolute Risk Contribution", ascending=False).drop(
            columns=["Absolute Risk Contribution"])
        df.reset_index(drop=True, inplace=True)
        df["Risk Contribution"] = df["Risk Contribution"].apply(
            lambda x: f"{x:.2f}")
        df = df[df["Risk Contribution"].apply(lambda x: abs(float(x)) > 0.02)]

        if len(df) > 9 and shorten_table:
            top_df = df.iloc[:9].copy()
            others_sum = df.iloc[9:]["Risk Contribution"].astype(float).sum()
            others_row = {
                "Parameter": "Others",
                "Raw Value": "",
                "Risk Contribution": f"{others_sum:.2f}",
                "Description": "<div style='font-size: 0.7em; color: #AAAAAA;'>Combined contribution of other less influential parameters.</div>",
                "Comparison": ""
            }
            others_df = pd.DataFrame([others_row])
            df = pd.concat([top_df, others_df], ignore_index=True)

        return df

    def scale_ml_data(self, static_df, timeseries_df):
        """
        Scales the static and timeseries data using the loaded scaler objects.
        Args:
            static_df (pd.DataFrame): Static data to be scaled.
            timeseries_df (pd.DataFrame): Timeseries data to be scaled.
        Returns:
            tuple: Scaled static and timeseries data as pandas DataFrames.
        """
        # Work on copies to avoid chained assignment issues
        static_df = static_df.copy()
        timeseries_df = timeseries_df.copy()

        #

        # For static data: exclude 'hadm_id' and scale numeric columns
        numeric_cols_static = static_df.select_dtypes(
            include=['int64', 'float64']).columns.drop('hadm_id', errors='ignore')
        static_scaled = self.static_scaler.transform(
            static_df.loc[:, numeric_cols_static].astype("float32"))
        scaled_static_df = pd.DataFrame(
            static_scaled, index=static_df.index, columns=numeric_cols_static)

        # Convert the target columns to float64 before assigning scaled data
        static_df.loc[:, numeric_cols_static] = static_df.loc[:,
                                                              numeric_cols_static].astype("float64")
        static_df.loc[:, numeric_cols_static] = scaled_static_df

        # For timeseries data: exclude 'hadm_id' and scale numeric columns
        numeric_cols_timeseries = timeseries_df.select_dtypes(
            include=['int64', 'float64']).columns.drop('hadm_id', errors='ignore')
        # ensure column order exactly matches what the scaler saw at fit time
        expected = list(self.timeseries_scaler.feature_names_in_)
        timeseries_df = timeseries_df.reindex(columns=expected)

        timeseries_scaled = self.timeseries_scaler.transform(
            timeseries_df.loc[:, numeric_cols_timeseries].astype("float32"))
        scaled_timeseries_df = pd.DataFrame(
            timeseries_scaled, index=timeseries_df.index, columns=numeric_cols_timeseries)

        # Convert the target columns to float64 before assigning scaled data
        timeseries_df.loc[:, numeric_cols_timeseries] = timeseries_df.loc[:,
                                                                          numeric_cols_timeseries].astype("float64")
        # Assign the scaled data back to the original DataFrame
        timeseries_df.loc[:, numeric_cols_timeseries] = scaled_timeseries_df

        return static_df, timeseries_df

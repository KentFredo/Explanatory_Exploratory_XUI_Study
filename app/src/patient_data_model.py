import pandas as pd
import streamlit as st
import numpy as np


class Patient:
    def __init__(self):
        self.demographics = {
            "age": None,
            "weight": None,
            "race_white": None,
            "race_black": None,
            "race_hispanic": None,
            "race_other": None,
            "gender_F": None,
            "gender_M": None,
            "ethnicity": None,
            "gender": None
        }
        self.scores = {
            "sofa": None,
            "sirs": None,
            "mingcs": None,
            "elixhauser_hospital": None
        }
        self.diagnosis = {
            "Cancer/Malignancy": None,
            "Cardiovascular": None,
            "Gastrointestinal": None,
            "Hematologic": None,
            "Hepatic": None,
            "Metabolic/Endocrine": None,
            "Musculoskeletal": None,
            "Neurological": None,
            "Other": None,
            "Renal": None,
            "Respiratory": None,
            "Sepsis/Infection": None,
            "Trauma/Injury": None
        }
        self.specimen = {
            "Blood/Serology": None,
            "Other": None,
            "Respiratory/Swab": None,
            "Urine": None
        }
        self.clinical_data = {
            "suspected_infection_time_poe_days": None,
            "positiveculture_poe": None,
            "blood_culture_positive": None,
            "septic_shock_explicit": None,
            "severe_sepsis_explicit": None,
            "vent": None
        }
        self.laboratory = pd.DataFrame()
        self.vitals = pd.DataFrame({
            "heartrate": [None] * 24,
            "sysbp": [None] * 24,
            "diasbp": [None] * 24,
            "meanbp": [None] * 24,
            "resprate": [None] * 24,
            "tempc": [None] * 24,
            "spo2": [None] * 24
        })
        self.vasopressor = pd.DataFrame({
            "vasopressor_data": [None]
        })
        self.urineoutput = pd.DataFrame({
            "urineoutput": [None]
        })
        # Add ml_data attribute to store ML data of this patient object
        self.ml_data = {"static": None, "timeseries": None, "y": None}

    def update_demographics(self, data):
        self.demographics.update(data)

        # Find Ethnicity and Gender
        if self.demographics['race_white'] == 1:
            self.demographics["ethnicity"] = "White"
        elif self.demographics['race_black'] == 1:
            self.demographics["ethnicity"] = "Black"
        elif self.demographics['race_hispanic'] == 1:
            self.demographics["ethnicity"] = "Hispanic"
        elif self.demographics['race_other'] == 1:
            self.demographics["ethnicity"] = "Other"

        if self.demographics['gender_F'] == 1:
            self.demographics["gender"] = "Female"
        elif self.demographics['gender_M'] == 1:
            self.demographics["gender"] = "Male"

    def update_scores(self, data):
        self.scores.update(data)

    def update_diagnosis(self, data):
        self.diagnosis.update(data)

    def update_specimen(self, data):
        self.specimen.update(data)

    def update_clinical_data(self, data):
        self.clinical_data.update(data)

    def update_laboratory(self, labs):
        self.laboratory = labs

    def update_laboratory_df(self, df):
        self.laboratory = df

    def update_vitals(self, data):
        self.vitals = pd.DataFrame(data)

    def update_vasopressor(self, data):
        self.vasopressor = pd.DataFrame(data)

    def update_urineoutput(self, data):
        self.urineoutput = pd.DataFrame(data)

    def update_ml_data(self, data):
        self.ml_data.update(data)

    def get_ml_data(self):
        return self.ml_data

    def to_dict(self):
        lab_dicts = {lab: df.to_dict() for lab, df in self.laboratory.items()}
        return {
            "demographics": self.demographics,
            "scores": self.scores,
            "diagnosis": self.diagnosis,
            "specimen": self.specimen,
            "clinical_data": self.clinical_data,
            "laboratory": lab_dicts,
            "vitals": self.vitals.to_dict(),
            "vasopressor": self.vasopressor.to_dict(),
            "urineoutput": self.urineoutput.to_dict()
        }

    def get_vital_average(self, feature_name):
        """
        Provides the average value of a vital sign feature.

        Args:
            feature_name (str): Name of the vital sign feature.

        Returns:
            Average value of the feature or None if not found.
        """
        if feature_name in self.vitals.columns:
            # Convert values to numeric and drop any non-numeric entries (None/NaN)
            values = pd.to_numeric(
                self.vitals[feature_name], errors="coerce").dropna()
            if not values.empty:
                if not feature_name == "tempc":
                    return int(values.mean())
                else:
                    return round(values.mean(), 1)
        return None

    def get_urineoutput_average(self):
        """
        Provides the average value of the urine output feature.

        Returns:
            Average value of urine output or None if not found.
        """
        if "urineoutput" in self.urineoutput.columns:
            # Convert values to numeric and drop any non-numeric entries (None/NaN)
            values = pd.to_numeric(
                self.urineoutput["urineoutput"], errors="coerce").dropna()
            if not values.empty:
                return int(values.mean())
        return None

    def get_vasopressor_average(self, feature_name):
        """
        Provides the average value of the vasopressor feature.

        Returns:
            Average value of vasopressor or None if not found.
        """
        if feature_name in self.vasopressor.columns:
            # Convert values to numeric and drop any non-numeric entries (None/NaN)
            values = pd.to_numeric(
                self.vasopressor[feature_name], errors="coerce").dropna()
            if not values.empty:
                return round(values.mean(), 2)
        return None

    def get_feature_value(self, feature_name):
        """
        Provides the value of a feature based on the feature name.
        For timeseries features (vitals, vasopressor, urineoutput), returns the average.

        Args:
            feature_name (str): Name of the feature.

        Returns:
            Value of the feature or None if not found.
        """
        if feature_name in self.demographics:
            return self.demographics.get(feature_name)
        elif feature_name in self.scores:
            return self.scores.get(feature_name)
        elif feature_name in self.clinical_data:
            return self.clinical_data.get(feature_name)
        elif feature_name in self.specimen:
            return self.specimen.get(feature_name)
        elif feature_name.startswith("diagnosis_"):
            diagnosis_key = feature_name[len("diagnosis_"):]
            return self.diagnosis.get(diagnosis_key)
        elif feature_name.startswith("specimen_group_"):
            specimen_key = feature_name[len("specimen_group_"):]
            return self.specimen.get(specimen_key)
        elif any(feature_name.endswith(suffix) for suffix in ["_count", "_mean", "_max", "_min", "_slope"]):
            for suffix in ["_count", "_mean", "_max", "_min", "_slope"]:
                if feature_name.endswith(suffix):
                    base_feature = feature_name[:-len(suffix)]
                    column_name = suffix.lstrip("_")
                    if base_feature in self.laboratory.index and column_name in self.laboratory.columns:
                        return self.laboratory.loc[base_feature, column_name]
                    else:
                        return None
        elif any(feature_name.startswith(prefix) for prefix in ["heartrate", "sysbp", "diasbp", "meanbp", "resprate", "tempc", "spo2"]):
            vital_mean = self.get_vital_average(feature_name)
            return vital_mean
        elif any(feature_name.startswith(prefix) for prefix in ["dobutamine", "dopamine", "epinephrine", "norepinephrine", "phenylephrine", "vasopressin"]):
            vasopressor_mean = self.get_vasopressor_average(feature_name)
            return vasopressor_mean
        elif feature_name.startswith("urineoutput"):
            urineoutput_mean = self.get_urineoutput_average()
            return urineoutput_mean
        else:
            return None

    def get_feature_unit(self, feature: str) -> str:
        """
        Returns the unit for the given feature from the session state's feature_metadata dictionary.
        If the feature is not found or is NaN, an empty string is returned.
        """
        if "feature_metadata" in st.session_state:
            unit = st.session_state.feature_metadata.get(
                feature, {}).get("unit", "")
            if pd.isna(unit):
                return ""
            return unit
        else:
            return ""

    def update_feature_with_scaling(self, data_type, feature_name, absolute_value):
        """
        Adjusts the specified feature in the given data source so that its new average becomes close to absolute_value.
        It finds a multiplicative scale (applied to each original value and then clipped to the original bounds)
        so that the average of the new values is as close as possible to absolute_value.

        The data_type should be one of: "vitals", "urineoutput", or "vasopressor".

        For "vitals", if feature_name is "tempc", values are rounded to 1 decimal place; otherwise, values are set as int.
        For "urineoutput" and "vasopressor", values are set as int (with vasopressor rounded to 2 decimals if needed).

        Args:
            data_type (str): One of "vitals", "urineoutput", or "vasopressor" indicating which dataframe to update.
            feature_name (str): Name of the feature within the specified dataframe.
            absolute_value (float): The desired new average value for the feature.
        """
        # Select the appropriate DataFrame based on data_type
        if data_type == "vitals":
            df = self.vitals
        elif data_type == "urineoutput":
            df = self.urineoutput
        elif data_type == "vasopressor":
            df = self.vasopressor
        else:
            return

        if feature_name not in df.columns:
            return

        # Work with float values and make a copy
        series = df[feature_name].astype(float).copy()
        orig = series.copy()

        # Use global bounds from st.session_state.patient_base via get_feature_statistics
        stats = st.session_state.patient_base.get_feature_statistics(
            feature_name)
        lower_bound = stats["min"]
        upper_bound = stats["max"]

        # Current mean
        old_mean = orig.mean()

        # If the series is constant or very close to zero mean for vasopressor, set every value to absolute_value.
        if data_type == "vasopressor" and abs(old_mean) < 1e-9:
            new_series = pd.Series(
                [absolute_value] * len(orig), index=orig.index)
            new_series = new_series.round(2)
            df[feature_name] = new_series
            return
        elif abs(old_mean) < 1e-9:
            return

        # Helper function to compute the average after applying a scale and clipping
        def clipped_avg(scale_factor):
            scaled = (orig * scale_factor).clip(lower_bound, upper_bound)
            return scaled.mean()

        # Binary search over a range of possible scale factors
        tol = 1e-4
        low = 0.0
        naive_ratio = absolute_value / old_mean
        high = max(naive_ratio * 10, 10)
        scale = 1.0
        for _ in range(100):
            mid = (low + high) / 2
            avg_mid = clipped_avg(mid)
            if abs(avg_mid - absolute_value) < tol:
                scale = mid
                break
            if avg_mid < absolute_value:
                low = mid
            else:
                high = mid
            scale = mid

        # Apply the determined scale and clip to bounds
        new_series = (orig * scale).clip(lower_bound, upper_bound)

        # Convert values: for "tempc" in vitals round to 1 decimal place, for vasopressor round to 2 decimals, for others convert to int.
        if data_type == "vitals" and feature_name == "tempc":
            new_series = new_series.round(1)
        elif data_type == "vasopressor":
            new_series = new_series.round(2)
        else:
            new_series = new_series.round().astype(int)

        # Update the appropriate DataFrame
        df[feature_name] = new_series

    def update_vitals_average(self, new_average):
        """
        Update the average value of a vital sign feature.

        Args:
            new_average (dict): Dictionary containing the new average values for each vital sign.
        """
        for key, value in new_average.items():
            if key in self.vitals.columns:
                self.vitals[key] = value

    def convert_to_ml_data(self):
        """
        Converts all raw patient data into the machine learning data format.
        Builds numpy arrays for static features and a (1, 24, n_features) timeseries tensor.
        """
        import numpy as np
        import pandas as pd
        import streamlit as st

        # 1) STATIC FEATURES ---------------------------------------------------
        static_vals = [
            self.get_feature_value(f)
            for f in st.session_state.static_feature_names
        ]
        ordered_static_df = pd.DataFrame(
            [static_vals],
            columns=st.session_state.static_feature_names
        )

        # 2) TIMESERIES FEATURES ------------------------------------------------
        #   a) merge raw dataframes
        merged = pd.concat(
            [self.vitals, self.urineoutput, self.vasopressor],
            axis=1
        )
        ordered_ts_df = merged[st.session_state.timeseries_feature_names]

        #   b) flatten in FEATURE‑MAJOR order: feature_0…feature_23, next_feature_0…_23, …
        n_hours = 24
        flattened = {}
        for feature in ordered_ts_df.columns:
            for hour in range(n_hours):
                flattened[f"{feature}_{hour}"] = ordered_ts_df.at[hour, feature]
        ts_flat_df = pd.DataFrame([flattened])  # shape (1, 24 * n_features)

        #   c) align columns exactly to what the scaler saw at fit time
        scaler = st.session_state.sepsis_prediction_model.timeseries_scaler
        expected_cols = list(scaler.feature_names_in_)
        ts_flat_df = ts_flat_df.reindex(columns=expected_cols)

        # 3) SCALE BOTH STATIC & TIMESERIES -------------------------------------
        scaled_static_df, scaled_ts_flat_df = (
            st.session_state.sepsis_prediction_model
            .scale_ml_data(ordered_static_df, ts_flat_df)
        )
        # fill missing, cast
        scaled_static = (
            scaled_static_df
            .fillna(-1)
            .astype(np.float32)
            .to_numpy()
        )
        scaled_ts_flat = (
            scaled_ts_flat_df
            .fillna(-1)
            .astype(np.float32)
        )

        # 4) RESHAPE TIMESERIES INTO (1, 24, n_features) ------------------------
        n_features = len(ordered_ts_df.columns)
        total_cols = scaled_ts_flat.shape[1]
        assert total_cols == n_hours * n_features, (
            f"Expected {n_hours}×{n_features}={n_hours*n_features} cols, "
            f"got {total_cols}"
        )

        # scaled_ts_flat is feature-major, so first reshape to (n_features, n_hours)
        arr = scaled_ts_flat.to_numpy().reshape(n_features, n_hours)
        # then transpose to (n_hours, n_features) and add batch-dim
        timeseries_array = arr.T[np.newaxis, :, :]

        # 5) SAVE INTO self.ml_data ---------------------------------------------
        self.ml_data["static"] = scaled_static
        self.ml_data["timeseries"] = timeseries_array

    @classmethod
    def from_dict(cls, data):
        patient = cls()
        patient.demographics = data.get("demographics", {})
        patient.scores = data.get("scores", {})
        patient.diagnosis = data.get("diagnosis", {})
        patient.specimen = data.get("specimen", {})
        patient.clinical_data = data.get("clinical_data", {})
        lab_dicts = data.get("laboratory", {})
        patient.laboratory = {lab: pd.DataFrame(
            df) for lab, df in lab_dicts.items()}
        patient.vitals = pd.DataFrame(data.get("vitals", {}))
        patient.vasopressor = pd.DataFrame(data.get("vasopressor", {}))
        patient.urineoutput = pd.DataFrame(data.get("urineoutput", {}))
        return patient

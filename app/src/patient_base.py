import pandas as pd


class PatientBase:
    def __init__(self):
        self._df = None

    def set_dataframe(self, df: pd.DataFrame):
        """
        Set the dataframe containing patient base statistics.

        Parameters:
            df (pd.DataFrame): DataFrame with statistic aspects as row index and features as columns.
        """
        self._df = df

    def get_available_features(self, exclusion_list: list = None) -> list:
        """
        Get the list of available features (columns) in the dataframe,
        optionally excluding specified features and those matching default patterns.

        Parameters:
            exclusion_list (list, optional): List of additional feature names to exclude.

        Returns:
            list: List of feature names (columns) after applying exclusions.
        """
        if self._df is None:
            raise ValueError(
                "Dataframe is not set. Please set it using set_dataframe().")
        features = self._df.columns.tolist()

        # Exclude features that start with "hadm_id", contain "race_", "diagnosis_", "specimen_",
        # or match any feature in the additional exclusions list.
        def should_exclude(feature):
            # List for exact feature exclusions; add more values as needed.
            additional_exclusions = [
                "positiveculture_poe",
                "suspected_infection_time_poe_days",
                "positiveculture_poe",
                "blood_culture_positive",
                "vent",
                "septic_shock_explicit",
                "severe_sepsis_explicit",
                "gender_F",
                "gender_M",
                "elixhauser_hospital",
            ]
            # Exclude if feature starts with "hadm_id"
            if feature.startswith("hadm_id"):
                return True
            # Exclude if feature contains unwanted substrings.
            for pattern in ["race_", "diagnosis_", "specimen_"]:
                if pattern in feature:
                    return True
            # Exclude if feature is in the additional exclusions list.
            if feature in additional_exclusions:
                return True
            return False

        # Use the provided exclusion list if any; otherwise, use an empty list.
        additional_exclusions = exclusion_list if exclusion_list is not None else []

        filtered_features = []
        for feature in features:
            if should_exclude(feature):
                continue
            if feature in additional_exclusions:
                continue
            filtered_features.append(feature)
        return filtered_features

    def get_feature_value(self, feature: str, statistic: str):
        """
        Get the value for a given feature and statistic.

        Parameters:
            feature (str): The feature (column) name.
            statistic (str): The statistic aspect (e.g., "min", "max",
                             "survivors_lower", "survivors_upper",
                             "non_survivors_lower", "non_survivors_upper").

        Returns:
            The corresponding statistic value.

        Raises:
            ValueError: If the dataframe is not set or if the feature or statistic does not exist.
        """
        if self._df is None:
            raise ValueError(
                "Dataframe is not set. Please set it using set_dataframe().")

        # Map caller's statistic request to the dataframe row index keys.
        # Assumes dataframe index keys are:
        # "min", "max", "survivor_lower", "survivor_upper",
        # "non_survivor_lower", "non_survivor_upper"
        statistic_mapping = {
            "min": "min",
            "max": "max",
            "survivors_lower": "survivor_lower",
            "survivors_upper": "survivor_upper",
            "survivors_mean": "survivor_mean",
            "non_survivors_lower": "non_survivor_lower",
            "non_survivors_upper": "non_survivor_upper",
            "non_survivors_mean": "non_survivor_mean"
        }

        if statistic not in statistic_mapping:
            raise ValueError(
                f"Statistic '{statistic}' not recognized. Valid keys are: {list(statistic_mapping.keys())}")

        row_key = statistic_mapping[statistic]

        if feature not in self._df.columns:
            raise ValueError(
                f"Feature '{feature}' not found in dataframe columns.")

        if row_key not in self._df.index:
            raise ValueError(
                f"Statistic '{row_key}' not found in dataframe index.")

        return self._df.at[row_key, feature]

    def get_feature_statistics(self, feature: str) -> dict:
        """
        Get all statistic values for a given feature as a dictionary.

        Parameters:
            feature (str): The feature (column) name.

        Returns:
            dict: A dictionary where each key is one of "min", "max",
                  "survivors_lower", "survivors_upper", "non_survivors_lower",
                  "non_survivors_upper", and its value is the corresponding statistic.

        Raises:
            ValueError: If the dataframe is not set or if the feature or any statistic does not exist.
        """
        if self._df is None:
            raise ValueError(
                "Dataframe is not set. Please set it using set_dataframe().")

        if feature not in self._df.columns:
            print(self._df.columns)
            raise ValueError(
                f"Feature '{feature}' not found in dataframe columns.")

        statistic_mapping = {
            "min": "min",
            "max": "max",
            "survivors_lower": "survivor_lower",
            "survivors_upper": "survivor_upper",
            "non_survivors_lower": "non_survivor_lower",
            "non_survivors_upper": "non_survivor_upper"
        }

        result = {}
        for key, row_key in statistic_mapping.items():
            if row_key not in self._df.index:
                raise ValueError(
                    f"Statistic '{row_key}' not found in dataframe index.")
            result[key] = self._df.at[row_key, feature]
        return result

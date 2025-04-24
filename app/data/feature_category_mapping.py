FEATURE_CATEGORY_MAPPING = {
    "Demographics": list(range(0, 6)) + list(range(161, 163)),
    "Clinical": list(range(6, 16)) + list(range(163, 179)),
    "Lab": list(range(16, 161))
}

TIMESERIES_FEATURE_MAPPING = {
    "Vital Signs": ["heartrate", "sysbp", "diasbp", "meanbp", "resprate", "tempc", "spo2"],
    "Urine Output": ["urineoutput"],
    "Vasopressor": [
        "dobutamine_dose", "dopamine_dose",
        "vasopressin_dose", "phenylephrine_dose",
        "epinephrine_dose", "norepinephrine_dose"
    ]
}

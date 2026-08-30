# Extracted from the original DataCamp/DataLab project workbook.
# Raw course-provided datasets are not redistributed in this public portfolio.

import pandas as pd


def merge_all_data(user_health_file, supplement_file, experiments_file, user_profiles_file):
    health = pd.read_csv(user_health_file)
    supplements = pd.read_csv(supplement_file)
    experiments = pd.read_csv(experiments_file)
    profiles = pd.read_csv(user_profiles_file)

    health["date"] = pd.to_datetime(health["date"])
    supplements["date"] = pd.to_datetime(supplements["date"])
    health["sleep_hours"] = (
        health["sleep_hours"].astype(str).str.extract(r"([\d.]+)").astype(float)
    )

    supplements = supplements.merge(
        experiments[["experiment_id", "name"]],
        on="experiment_id",
        how="left",
    )
    supplements.rename(columns={"name": "experiment_name"}, inplace=True)
    supplements["dosage_grams"] = supplements["dosage"]
    mg_mask = supplements["dosage_unit"].str.lower().eq("mg")
    supplements.loc[mg_mask, "dosage_grams"] = supplements.loc[mg_mask, "dosage"] / 1000

    supplements = supplements[[
        "user_id", "date", "supplement_name", "dosage_grams",
        "is_placebo", "experiment_name"
    ]]

    df = health.merge(supplements, on=["user_id", "date"], how="left")
    df["supplement_name"] = df["supplement_name"].fillna("No intake")
    df = df.merge(profiles, on="user_id", how="left")

    def get_age_group(age):
        if pd.isna(age):
            return "Unknown"
        if age < 18:
            return "Under 18"
        if age <= 25:
            return "18-25"
        if age <= 35:
            return "26-35"
        if age <= 45:
            return "36-45"
        if age <= 55:
            return "46-55"
        if age <= 65:
            return "56-65"
        return "Over 65"

    df["user_age_group"] = df["age"].apply(get_age_group)

    return df[[
        "user_id", "date", "email", "user_age_group", "experiment_name",
        "supplement_name", "dosage_grams", "is_placebo", "average_heart_rate",
        "average_glucose", "sleep_hours", "activity_level"
    ]]

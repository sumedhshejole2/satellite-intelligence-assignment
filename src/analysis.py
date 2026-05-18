import pandas as pd
import numpy as np

# =========================================================
# LOAD CLEANED DATASET
# =========================================================

print("\n==============================")
print("LOADING CLEANED DATASET")
print("==============================")

df = pd.read_csv(
    "data/cleaned_parcel_timeseries.csv"
)

# =========================================================
# PARSE DATES
# =========================================================

print("\n==============================")
print("PARSING DATES")
print("==============================")

df["date"] = pd.to_datetime(df["date"])
df["sowing_date"] = pd.to_datetime(df["sowing_date"])

# =========================================================
# FILTER GOOD SENSOR ROWS
# =========================================================

print("\n==============================")
print("FILTERING GOOD SENSOR ROWS")
print("==============================")

initial_rows = len(df)

df = df[
    df["sensor_status"] == "ok"
].copy()

filtered_rows = len(df)

print(
    f"Removed bad/unknown sensor rows: "
    f"{initial_rows - filtered_rows}"
)

# =========================================================
# CALCULATE DAYS FROM SOWING
# =========================================================

print("\n==============================")
print("CALCULATING DAYS FROM SOWING")
print("==============================")

df["days_from_sowing"] = (
    df["date"] - df["sowing_date"]
).dt.days

print(df[
    [
        "parcel_id",
        "date",
        "sowing_date",
        "days_from_sowing"
    ]
].head())

# =========================================================
# CREATE BEFORE WINDOW
# (-30 to -1 days)
# =========================================================

print("\n==============================")
print("CREATING BEFORE WINDOW")
print("==============================")

before_df = df[
    (df["days_from_sowing"] >= -30) &
    (df["days_from_sowing"] < 0)
]

print(f"Before window rows: {len(before_df)}")

# =========================================================
# CREATE AFTER WINDOW
# (1 to 30 days)
# =========================================================

print("\n==============================")
print("CREATING AFTER WINDOW")
print("==============================")

after_df = df[
    (df["days_from_sowing"] > 0) &
    (df["days_from_sowing"] <= 30)
]

print(f"After window rows: {len(after_df)}")

# =========================================================
# COMPUTE MEAN NDVI BEFORE SOWING
# =========================================================

print("\n==============================")
print("COMPUTING BEFORE NDVI")
print("==============================")

before_summary = (
    before_df
    .groupby("crop_type")["ndvi_value"]
    .mean()
    .reset_index()
)

before_summary.rename(
    columns={
        "ndvi_value": "mean_ndvi_before"
    },
    inplace=True
)

print(before_summary)

# =========================================================
# COMPUTE MEAN NDVI AFTER SOWING
# =========================================================

print("\n==============================")
print("COMPUTING AFTER NDVI")
print("==============================")

after_summary = (
    after_df
    .groupby("crop_type")["ndvi_value"]
    .mean()
    .reset_index()
)

after_summary.rename(
    columns={
        "ndvi_value": "mean_ndvi_after"
    },
    inplace=True
)

print(after_summary)

# =========================================================
# COUNT UNIQUE PARCELS
# =========================================================

print("\n==============================")
print("COUNTING UNIQUE PARCELS")
print("==============================")

parcel_counts = (
    df
    .groupby("crop_type")["parcel_id"]
    .nunique()
    .reset_index()
)

parcel_counts.rename(
    columns={
        "parcel_id": "n_parcels"
    },
    inplace=True
)

print(parcel_counts)

# =========================================================
# MERGE FINAL SUMMARY
# =========================================================

print("\n==============================")
print("BUILDING FINAL SUMMARY")
print("==============================")

summary_df = (
    before_summary
    .merge(
        after_summary,
        on="crop_type",
        how="outer"
    )
    .merge(
        parcel_counts,
        on="crop_type",
        how="outer"
    )
)

# =========================================================
# ROUND VALUES
# =========================================================

summary_df["mean_ndvi_before"] = (
    summary_df["mean_ndvi_before"]
    .round(3)
)

summary_df["mean_ndvi_after"] = (
    summary_df["mean_ndvi_after"]
    .round(3)
)

# =========================================================
# SORT RESULTS
# =========================================================

summary_df = summary_df.sort_values(
    by="crop_type"
)

# =========================================================
# DISPLAY FINAL RESULTS
# =========================================================

print("\n==============================")
print("FINAL ANALYSIS OUTPUT")
print("==============================")

print(summary_df)

# =========================================================
# SAVE RESULTS
# =========================================================

print("\n==============================")
print("SAVING RESULTS")
print("==============================")

output_path = "outputs/crop_ndvi_summary.csv"

summary_df.to_csv(
    output_path,
    index=False
)

print(f"Saved analysis results to: {output_path}")

# =========================================================
# INTERPRETATION
# =========================================================

print("\n==============================")
print("INTERPRETATION")
print("==============================")

print("""
1. NDVI values generally increase after sowing,
   which suggests increasing vegetation growth.

2. Differences across crop types may reflect
   varying crop growth cycles and canopy development.

3. Results should be interpreted cautiously for
   crop types with smaller parcel counts.
""")

# =========================================================
# COMPLETE
# =========================================================

print("\n==============================")
print("ANALYSIS COMPLETE")
print("==============================")
import pandas as pd
import numpy as np

# =========================================================
# LOAD DATA
# =========================================================

print("\n==============================")
print("LOADING DATA")
print("==============================")

readings = pd.read_csv("data/parcel_readings.csv")
metadata = pd.read_csv("data/parcel_metadata.csv")

# =========================================================
# PARSE DATES
# =========================================================

print("\n==============================")
print("PARSING DATES")
print("==============================")

readings["date"] = pd.to_datetime(
    readings["date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

metadata["sowing_date"] = pd.to_datetime(
    metadata["sowing_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

# =========================================================
# CLEAN SENSOR STATUS
# =========================================================

print("\n==============================")
print("CLEANING SENSOR STATUS")
print("==============================")

readings["sensor_status"] = (
    readings["sensor_status"]
    .astype(str)
    .str.strip()
    .str.lower()
)

status_map = {
    "ok": "ok",
    "error": "bad",
    "nan": "unknown"
}

readings["sensor_status"] = (
    readings["sensor_status"]
    .map(status_map)
    .fillna("unknown")
)

print(
    readings["sensor_status"]
    .value_counts()
)

# =========================================================
# REMOVE INVALID NDVI VALUES
# =========================================================

print("\n==============================")
print("REMOVING INVALID NDVI VALUES")
print("==============================")

initial_rows = len(readings)

readings = readings[
    readings["ndvi_value"].between(-1, 1)
]

removed_ndvi = initial_rows - len(readings)

print(f"Removed invalid NDVI rows: {removed_ndvi}")

# =========================================================
# REMOVE INVALID DATES
# =========================================================

print("\n==============================")
print("REMOVING INVALID DATES")
print("==============================")

before_dates = len(readings)

readings = readings.dropna(subset=["date"])
metadata = metadata.dropna(subset=["sowing_date"])

after_dates = len(readings)

print(
    f"Removed rows with invalid dates: "
    f"{before_dates - after_dates}"
)

# =========================================================
# REMOVE DUPLICATES
# =========================================================

print("\n==============================")
print("REMOVING DUPLICATES")
print("==============================")

before_duplicates = len(readings)

readings = readings.drop_duplicates(
    subset=["parcel_id", "date"]
)

after_duplicates = len(readings)

print(
    f"Removed duplicate rows: "
    f"{before_duplicates - after_duplicates}"
)

# =========================================================
# REMOVE INVALID AREA VALUES
# =========================================================

print("\n==============================")
print("REMOVING INVALID AREA VALUES")
print("==============================")

before_area = len(metadata)

metadata = metadata[
    metadata["area_hectares"] > 0
]

after_area = len(metadata)

print(
    f"Removed invalid area rows: "
    f"{before_area - after_area}"
)

# =========================================================
# JOIN DATASETS
# =========================================================

print("\n==============================")
print("JOINING DATASETS")
print("==============================")

final_df = readings.merge(
    metadata,
    on="parcel_id",
    how="left"
)

print(f"Final dataset shape: {final_df.shape}")

# =========================================================
# CHECK MISSING METADATA AFTER JOIN
# =========================================================

print("\n==============================")
print("CHECKING JOIN RESULTS")
print("==============================")

missing_crop = final_df["crop_type"].isnull().sum()

print(
    f"Rows missing metadata after join: "
    f"{missing_crop}"
)

# =========================================================
# SORT DATA
# =========================================================

print("\n==============================")
print("SORTING DATA")
print("==============================")

final_df = final_df.sort_values(
    by=["parcel_id", "date"]
)

# =========================================================
# SAVE CLEANED DATASET
# =========================================================

print("\n==============================")
print("SAVING CLEANED DATASET")
print("==============================")

output_path = "data/cleaned_parcel_timeseries.csv"

final_df.to_csv(
    output_path,
    index=False
)

print(f"Saved cleaned dataset to: {output_path}")

# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n==============================")
print("PIPELINE COMPLETE")
print("==============================")

print(final_df.head())

print("\nCleaning pipeline completed successfully.")
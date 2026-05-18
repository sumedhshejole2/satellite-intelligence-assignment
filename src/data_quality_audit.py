import pandas as pd
import numpy as np

# =========================================================
# LOAD DATASETS
# =========================================================

print("\n==============================")
print("LOADING DATASETS")
print("==============================")

readings = pd.read_csv("data/parcel_readings.csv")
metadata = pd.read_csv("data/parcel_metadata.csv")

# =========================================================
# BASIC PREVIEW
# =========================================================

print("\n==============================")
print("READINGS HEAD")
print("==============================")
print(readings.head())

print("\n==============================")
print("METADATA HEAD")
print("==============================")
print(metadata.head())

# =========================================================
# DATASET SHAPES
# =========================================================

print("\n==============================")
print("DATASET SHAPES")
print("==============================")

print(f"Readings shape: {readings.shape}")
print(f"Metadata shape: {metadata.shape}")

# =========================================================
# COLUMN NAMES
# =========================================================

print("\n==============================")
print("READINGS COLUMNS")
print("==============================")
print(readings.columns.tolist())

print("\n==============================")
print("METADATA COLUMNS")
print("==============================")
print(metadata.columns.tolist())

# =========================================================
# DATA TYPES
# =========================================================

print("\n==============================")
print("READINGS INFO")
print("==============================")
print(readings.info())

print("\n==============================")
print("METADATA INFO")
print("==============================")
print(metadata.info())

# =========================================================
# DESCRIPTIVE STATISTICS
# =========================================================

print("\n==============================")
print("READINGS DESCRIBE")
print("==============================")
print(readings.describe(include="all"))

print("\n==============================")
print("METADATA DESCRIBE")
print("==============================")
print(metadata.describe(include="all"))

# =========================================================
# MISSING VALUES
# =========================================================

print("\n==============================")
print("MISSING VALUES COUNT")
print("==============================")

print("\nReadings missing values:")
print(readings.isnull().sum())

print("\nMetadata missing values:")
print(metadata.isnull().sum())

# =========================================================
# MISSING VALUE PERCENTAGES
# =========================================================

print("\n==============================")
print("MISSING VALUE PERCENTAGES")
print("==============================")

readings_missing_pct = (
    readings.isnull().mean() * 100
).round(2)

metadata_missing_pct = (
    metadata.isnull().mean() * 100
).round(2)

print("\nReadings missing percentages:")
print(readings_missing_pct)

print("\nMetadata missing percentages:")
print(metadata_missing_pct)

# =========================================================
# DUPLICATE ROWS
# =========================================================

print("\n==============================")
print("DUPLICATE ROWS")
print("==============================")

readings_duplicates = readings.duplicated().sum()
metadata_duplicates = metadata.duplicated().sum()

print(f"Readings duplicate rows: {readings_duplicates}")
print(f"Metadata duplicate rows: {metadata_duplicates}")

# =========================================================
# DUPLICATE BUSINESS KEYS
# =========================================================

print("\n==============================")
print("DUPLICATE PARCEL_ID + DATE")
print("==============================")

duplicate_keys = readings.duplicated(
    subset=["parcel_id", "date"]
).sum()

print(f"Duplicate parcel_id-date rows: {duplicate_keys}")

# =========================================================
# SENSOR STATUS VALUES
# =========================================================

print("\n==============================")
print("SENSOR STATUS UNIQUE VALUES")
print("==============================")

print(readings["sensor_status"].unique())

# =========================================================
# INVALID NDVI VALUES
# =========================================================

print("\n==============================")
print("INVALID NDVI VALUES")
print("==============================")

invalid_ndvi = readings[
    (readings["ndvi_value"] < -1) |
    (readings["ndvi_value"] > 1)
]

print(f"Invalid NDVI count: {len(invalid_ndvi)}")

if len(invalid_ndvi) > 0:
    print("\nSample invalid NDVI rows:")
    print(invalid_ndvi.head())

# =========================================================
# NEGATIVE RAINFALL VALUES
# =========================================================

print("\n==============================")
print("NEGATIVE RAINFALL VALUES")
print("==============================")

negative_rainfall = readings[
    readings["rainfall_mm"] < 0
]

print(f"Negative rainfall count: {len(negative_rainfall)}")

if len(negative_rainfall) > 0:
    print("\nSample negative rainfall rows:")
    print(negative_rainfall.head())

# =========================================================
# TEMPERATURE OUTLIERS
# =========================================================

print("\n==============================")
print("TEMPERATURE OUTLIERS")
print("==============================")

temperature_outliers = readings[
    (readings["temperature_c"] < -50) |
    (readings["temperature_c"] > 60)
]

print(f"Temperature outlier count: {len(temperature_outliers)}")

if len(temperature_outliers) > 0:
    print("\nSample temperature outliers:")
    print(temperature_outliers.head())

# =========================================================
# INVALID AREA VALUES
# =========================================================

print("\n==============================")
print("INVALID AREA VALUES")
print("==============================")

invalid_area = metadata[
    metadata["area_hectares"] <= 0
]

print(f"Invalid area count: {len(invalid_area)}")

if len(invalid_area) > 0:
    print("\nSample invalid area rows:")
    print(invalid_area.head())

# =========================================================
# UNIQUE PARCEL COUNTS
# =========================================================

print("\n==============================")
print("UNIQUE PARCEL COUNTS")
print("==============================")

print(
    f"Unique parcels in readings: "
    f"{readings['parcel_id'].nunique()}"
)

print(
    f"Unique parcels in metadata: "
    f"{metadata['parcel_id'].nunique()}"
)

# =========================================================
# JOIN COVERAGE CHECK
# =========================================================

print("\n==============================")
print("JOIN COVERAGE CHECK")
print("==============================")

missing_metadata = set(
    readings["parcel_id"]
) - set(
    metadata["parcel_id"]
)

missing_readings = set(
    metadata["parcel_id"]
) - set(
    readings["parcel_id"]
)

print(
    f"Parcels in readings but missing in metadata: "
    f"{len(missing_metadata)}"
)

print(
    f"Parcels in metadata but missing in readings: "
    f"{len(missing_readings)}"
)

# =========================================================
# PARSE DATES
# =========================================================

print("\n==============================")
print("PARSING DATES")
print("==============================")

# Mixed formats in readings dataset
# Examples:
# 16/05/2026
# 2026-01-27

readings["date"] = pd.to_datetime(
    readings["date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# Metadata uses YYYY-MM-DD

metadata["sowing_date"] = pd.to_datetime(
    metadata["sowing_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

# =========================================================
# DATE PARSING FAILURES
# =========================================================

print("\n==============================")
print("DATE PARSING FAILURES")
print("==============================")

invalid_reading_dates = readings["date"].isnull().sum()
invalid_sowing_dates = metadata["sowing_date"].isnull().sum()

print(f"Invalid reading dates: {invalid_reading_dates}")
print(f"Invalid sowing dates: {invalid_sowing_dates}")

# =========================================================
# DATE RANGES
# =========================================================

print("\n==============================")
print("DATE RANGES")
print("==============================")

print(
    f"Readings min date: "
    f"{readings['date'].min()}"
)

print(
    f"Readings max date: "
    f"{readings['date'].max()}"
)

print(
    f"Sowing min date: "
    f"{metadata['sowing_date'].min()}"
)

print(
    f"Sowing max date: "
    f"{metadata['sowing_date'].max()}"
)

# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n==============================")
print("AUDIT COMPLETE")
print("==============================")

print("Data understanding phase completed successfully.")
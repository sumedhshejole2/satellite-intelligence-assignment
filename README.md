# Satellite Intelligence Assignment

## Overview

This project implements a small-scale satellite intelligence data engineering pipeline using parcel-level agricultural sensor data and parcel metadata.

The objective was to:

1. Audit raw datasets for data quality issues
2. Build a reproducible cleaning pipeline
3. Generate a cleaned parcel-level time-series dataset
4. Perform a simple NDVI analysis around crop sowing dates
5. Reflect on production-readiness considerations

The assignment simulates real-world agricultural data engineering challenges involving:

* messy upstream data
* inconsistent schemas
* mixed date formats
* sensor quality issues
* join mismatches
* time-series analysis

---

# Project Structure

```text
satellite-intelligence-assignment/
│
├── data/
│   ├── parcel_metadata.csv
│   ├── parcel_readings.csv
│   └── cleaned_parcel_timeseries.csv
│
├── outputs/
│   └── crop_ndvi_summary.csv
│
├── src/
│   ├── data_quality_audit.py
│   ├── clean_pipeline.py
│   └── analysis.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/sumedhshejole2/satellite-intelligence-assignment.git
cd satellite-intelligence-assignment
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Data Sources

## parcel_readings.csv

Daily parcel-level sensor readings.

Columns:

| Column        | Description            |
| ------------- | ---------------------- |
| parcel_id     | Parcel identifier      |
| date          | Observation date       |
| ndvi_value    | Vegetation index value |
| temperature_c | Mean daily temperature |
| rainfall_mm   | Daily rainfall         |
| sensor_status | Sensor health flag     |

---

## parcel_metadata.csv

Static parcel metadata.

Columns:

| Column        | Description           |
| ------------- | --------------------- |
| parcel_id     | Parcel identifier     |
| mill_id       | Sugar mill identifier |
| crop_type     | Crop category         |
| sowing_date   | Crop sowing date      |
| area_hectares | Parcel size           |

---

# Data Quality Audit

A detailed audit was performed before any transformations were applied.

## Summary of Issues

| Issue                                  | Prevalence                                           | Action Taken                         | Justification                            |
| -------------------------------------- | ---------------------------------------------------- | ------------------------------------ | ---------------------------------------- |
| Missing sensor_status values           | 137 rows (3.97%)                                     | Standardized as `unknown`            | Prevents ambiguous downstream logic      |
| Inconsistent sensor status labels      | Multiple variants (`OK`, `ok`, ` OK`, `ERROR`, etc.) | Normalized to `ok`, `bad`, `unknown` | Ensures consistent filtering logic       |
| Invalid NDVI values outside [-1,1]     | 104 rows                                             | Removed                              | Violates physical NDVI constraints       |
| Duplicate parcel_id + date rows        | 8 rows                                               | Removed duplicates                   | Preserves one row per parcel/date grain  |
| Mixed date formats in readings dataset | Present                                              | Explicit mixed-format parsing        | Prevents silent datetime corruption      |
| Parcel mismatches across datasets      | 2 parcel_ids missing metadata matches                | Preserved with left join             | Avoids dropping otherwise valid readings |
| Missing metadata matches               | Some rows after join                                 | Left as null after join              | Makes upstream mismatch visible          |

---

# Key Audit Findings

## 1. Mixed Date Formats

The `parcel_readings.csv` dataset contained multiple date formats:

Examples:

```text
16/05/2026
2026-01-27
```

This required explicit mixed-format parsing using:

```python
pd.to_datetime(..., format="mixed", dayfirst=True)
```

This is a common production issue in systems where multiple upstream sources contribute data.

---

## 2. Invalid NDVI Values

The assignment specified that valid NDVI values must fall within:

```text
[-1, 1]
```

104 rows violated this rule.

Examples included:

```text
1.832
1.665
-1.976
```

These rows were removed because they are physically invalid.

---

## 3. Sensor Status Inconsistency

Sensor status values were inconsistent:

```text
OK
ok
 OK
ERROR
Error
error
```

Values were standardized to:

```text
ok
bad
unknown
```

This simplified downstream filtering and analysis.

---

## 4. Join Integrity Issues

The readings dataset contained parcel IDs that did not exist in the metadata dataset.

Rather than dropping those rows, a left join was used so the issue remained visible and valid readings were retained.

---

# Cleaning Pipeline

The cleaning pipeline is implemented in:

```text
src/clean_pipeline.py
```

The pipeline performs the following steps:

1. Load raw CSV files
2. Parse dates using explicit formats
3. Normalize sensor status labels
4. Remove invalid NDVI values
5. Remove invalid dates
6. Remove duplicate parcel/date rows
7. Validate area values
8. Join readings with metadata
9. Sort the final dataset
10. Export cleaned dataset

---

# Cleaning Decisions

## Sensor Status Handling

Sensor statuses were normalized:

| Raw Value | Standardized Value |
| --------- | ------------------ |
| OK        | ok                 |
| ok        | ok                 |
| ERROR     | bad                |
| Error     | bad                |
| missing   | unknown            |

Rows with `bad` or `unknown` sensor statuses were excluded from the final analysis phase.

---

## NDVI Validation

Rows where:

```text
ndvi_value < -1
OR
ndvi_value > 1
```

were removed.

This enforced domain validity.

---

## Duplicate Handling

Duplicate rows at the business-key level:

```text
(parcel_id, date)
```

were removed to maintain one row per parcel per day.

---

## Join Strategy

A left join was used:

```python
readings.merge(metadata, how="left")
```

This ensured:

* no valid readings were discarded
* upstream metadata gaps remained visible
* downstream monitoring could identify missing joins

---

# Output Dataset

The final cleaned dataset is:

```text
data/cleaned_parcel_timeseries.csv
```

The dataset contains:

* cleaned readings
* normalized sensor statuses
* validated NDVI values
* parcel metadata
* parsed timestamps

---

# Analysis

The analysis is implemented in:

```text
src/analysis.py
```

## Objective

For each crop type:

* Compute mean NDVI during the 30 days BEFORE sowing
* Compute mean NDVI during the 30 days AFTER sowing
* Ignore bad or unknown sensor readings

---

# Analysis Methodology

## 1. Filter Good Sensors

Only rows where:

```text
sensor_status == "ok"
```

were included.

---

## 2. Calculate Days from Sowing

A relative time offset was computed:

```python
(date - sowing_date).dt.days
```

---

## 3. Define Time Windows

### Before Window

```text
-30 <= days_from_sowing < 0
```

### After Window

```text
0 < days_from_sowing <= 30
```

---

# Analysis Results

| crop_type | mean_ndvi_before | mean_ndvi_after | n_parcels |
| --------- | ---------------- | --------------- | --------- |
| soybean   | 0.211            | 0.308           | 4         |
| sugarcane | 0.224            | 0.352           | 19        |
| wheat     | 0.207            | 0.322           | 2         |

---

# Interpretation

Across all crop types, mean NDVI increased during the 30 days after sowing, which is consistent with expected vegetation growth following crop establishment.

Sugarcane showed the largest post-sowing NDVI increase, potentially reflecting denser canopy development and faster biomass accumulation relative to the other crops.

The wheat category contains only two parcels, so those results are less statistically reliable and should be interpreted cautiously.

---

# Production Readiness Reflection

## 1. What would change if the dataset became 100× larger?

### A. Move Beyond CSV Files

CSV processing does not scale efficiently.

I would move to:

* Parquet storage
* partitioned datasets
* columnar storage formats

Benefits:

* lower memory usage
* faster reads
* predicate pushdown
* better compression

---

### B. Distributed Processing

Pandas is appropriate for this assignment scale, but not for large production workloads.

I would migrate to:

* Spark
* Polars
* DuckDB

depending on workload characteristics.

---

### C. Workflow Orchestration

The pipeline would be orchestrated using:

* Airflow
* Dagster
* Prefect

This would provide:

* scheduling
* retries
* dependency management
* observability

---

## 2. What would be monitored in production?

I would monitor:

### Data Quality Metrics

* invalid NDVI rate
* missing sensor status rate
* duplicate row frequency
* missing metadata join rate
* schema drift

---

### Operational Metrics

* pipeline runtime
* ingestion latency
* failed job counts
* output row counts
* partition freshness

---

### Distribution Drift

I would also monitor:

* NDVI distribution shifts
* sensor status distribution changes
* unusual parcel volume spikes

These may indicate upstream system issues.

---

## 3. Most Likely Silent Failure

The most likely silent failure would be upstream schema or date-format drift.

The readings dataset already contained mixed date formats. If parsing assumptions changed silently upstream, time-series calculations could become corrupted without causing pipeline crashes.

This type of issue is especially dangerous because:

* pipelines may still run successfully
* downstream aggregates may appear plausible
* errors may only surface much later in analysis

---

# Engineering Tradeoffs

Several intentional tradeoffs were made:

| Decision                   | Tradeoff                                            |
| -------------------------- | --------------------------------------------------- |
| Remove invalid NDVI values | Simpler and safer than imputation                   |
| Use left join              | Preserves data visibility but leaves null metadata  |
| Normalize sensor statuses  | Reduces ambiguity but simplifies original semantics |
| Use Pandas                 | Fast development but limited scalability            |

---

# AI Tool Usage

ChatGPT was used to:

* brainstorm edge cases
* validate Pandas transformations
* improve pipeline structure
* refine README organization
* review production-readiness considerations

All code and outputs were manually reviewed and tested before submission.

---

# How to Run

## 1. Run Audit

```bash
python src/data_quality_audit.py
```

---

## 2. Run Cleaning Pipeline

```bash
python src/clean_pipeline.py
```

---

## 3. Run Analysis

```bash
python src/analysis.py
```

---

# Deliverables

This repository contains:

* data quality audit
* cleaning pipeline
* cleaned dataset
* NDVI analysis
* production reflection
* analysis outputs

---

# Loom Walkthrough

Loom video link:

```text

```

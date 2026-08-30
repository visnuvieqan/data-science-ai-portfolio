# Supplement Experiment Data Integration Pipeline

**Focus:** Data engineering, ETL, data transformation, and multi-source joins.

This project builds a reusable data integration function across health, supplement, experiment, and profile datasets.

## Work performed
- Combined health metrics, supplement usage, experiment metadata, and user profiles.
- Standardized dates and text-formatted measurements.
- Converted supplement dosage units and handled no-intake records.
- Implemented one-to-many joins and derived demographic features.
- Produced a standardized analytical dataset for downstream analysis.

## Validation
The integration function produced a **2,721-row, 12-column** analytical dataset with complete user IDs, dates, emails, and age groups in the reviewed run.

## Public repository files
- `etl.py` — extracted analysis/source code from the original workbook
- `README.md` — project scope, methods, and highlights

> **Data note:** The original project used course-provided datasets in DataCamp/DataLab. Those raw datasets and reference images are intentionally not redistributed in this public repository. The source code keeps the original expected filenames for reproducibility with an authorized local copy of the data.

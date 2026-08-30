# Recipe Site Traffic Prediction

**Focus:** Binary classification, model comparison, business metrics, and recommendations.

This project analyzes 947 recipe records and builds a model to predict which recipes are likely to generate high website traffic.

## Work performed
- Validated and cleaned numerical and categorical variables.
- Investigated missing values and prepared features for modeling.
- Performed exploratory data analysis.
- Built and compared Logistic Regression and Random Forest classifiers.
- Used stratified train/test validation and cross-validation.
- Evaluated accuracy, precision, recall, and F1 score.
- Selected precision as an important business metric because homepage placement is limited.
- Produced recommendations for deployment, monitoring, retraining, and A/B testing.

## Highlight
The Logistic Regression model achieved approximately **83.7% precision** on high-traffic predictions in the original practical exam workflow.

## Public repository files
- `analysis.py` — extracted analysis/source code from the original workbook
- `README.md` — project scope, methods, and highlights

> **Data note:** The original project used course-provided datasets in DataCamp/DataLab. Those raw datasets and reference images are intentionally not redistributed in this public repository. The source code keeps the original expected filenames for reproducibility with an authorized local copy of the data.

# Extracted from the original DataCamp/DataLab project workbook.
# Raw course-provided datasets are not redistributed in this public portfolio.

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    ConfusionMatrixDisplay,
    classification_report,
)

# Load dataset
df = pd.read_csv("recipe_site_traffic_2212.csv")
print("Dataset Shape:", df.shape)
print(df.info())
print(df.isnull().sum())

# Data validation and cleaning
print("Duplicate recipes:", df["recipe"].duplicated().sum())
print("Raw category values:", df["category"].unique())
df["category"] = df["category"].replace({"Chicken Breast": "Chicken"})

df["servings"] = df["servings"].astype(str).str.extract(r"(\d+)").astype(int)
num_cols = ["calories", "carbohydrate", "sugar", "protein"]
print("Skewness of numeric columns:")
print(df[num_cols].skew())
for col in num_cols:
    df[col] = df[col].fillna(df[col].median())

df["high_traffic"] = df["high_traffic"].fillna("Low")
print("Missing values after cleaning:")
print(df.isnull().sum())

# Exploratory analysis
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x="category", order=df["category"].value_counts().index)
plt.title("Distribution of Recipe Categories")
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(8, 5))
sns.histplot(df["calories"], bins=30, kde=True)
plt.title("Distribution of Calories")
plt.show()

plot_df = df.copy()
plot_df["high_traffic"] = plot_df["high_traffic"].replace({1: "High", 0: "Low"})
plt.figure(figsize=(12, 6))
sns.countplot(data=plot_df, x="category", hue="high_traffic")
plt.title("Recipe Category vs High Traffic")
plt.xticks(rotation=45)
plt.show()

# Prepare machine-learning data
df["high_traffic"] = df["high_traffic"].map({"High": 1, "Low": 0})
X = df.drop(columns=["recipe", "high_traffic"])
y = df["high_traffic"]
X = pd.get_dummies(X, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

numeric_features = ["calories", "carbohydrate", "sugar", "protein", "servings"]
preprocessor = ColumnTransformer(
    transformers=[("num", StandardScaler(), numeric_features)],
    remainder="passthrough",
)

logistic_model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(random_state=42)),
])
logistic_model.fit(X_train, y_train)

y_pred_log = logistic_model.predict(X_test)
print("Logistic Regression Performance")
print("Accuracy :", accuracy_score(y_test, y_pred_log))
print("Precision:", precision_score(y_test, y_pred_log))
print("Recall   :", recall_score(y_test, y_pred_log))
print("F1 Score :", f1_score(y_test, y_pred_log))
print("ROC AUC  :", roc_auc_score(y_test, y_pred_log))
print(classification_report(y_test, y_pred_log))

rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
print("Random Forest Performance")
print("Accuracy :", accuracy_score(y_test, y_pred_rf))
print("Precision:", precision_score(y_test, y_pred_rf))
print("Recall   :", recall_score(y_test, y_pred_rf))
print("F1 Score :", f1_score(y_test, y_pred_rf))
print("ROC AUC  :", roc_auc_score(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf))

# 5-fold stratified cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
log_cv_precision = cross_val_score(logistic_model, X, y, cv=cv, scoring="precision")
rf_cv_precision = cross_val_score(rf_model, X, y, cv=cv, scoring="precision")
print("Logistic Regression 5-fold precision: {:.2%} (+/- {:.2%})".format(
    log_cv_precision.mean(), log_cv_precision.std()
))
print("Random Forest 5-fold precision: {:.2%} (+/- {:.2%})".format(
    rf_cv_precision.mean(), rf_cv_precision.std()
))

ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred_log, display_labels=["Low Traffic", "High Traffic"]
)
plt.title("Logistic Regression Confusion Matrix")
plt.show()

# Coefficient inspection from the original workflow
coefficients = pd.DataFrame({
    "Feature": X_train.columns,
    "Coefficient": logistic_model.named_steps["classifier"].coef_[0],
}).sort_values(by="Coefficient", ascending=False)
print(coefficients.head(10))

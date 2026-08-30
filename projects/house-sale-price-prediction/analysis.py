# Extracted from the original DataCamp/DataLab project workbook.
# Raw course-provided datasets are not redistributed in this public portfolio.

import pandas as pd
import numpy as np

house_sales = pd.read_csv('house_sales.csv')
house_sales['city'] = house_sales['city'].replace('--', np.nan)
missing_city = house_sales['city'].isna().sum()
print(missing_city)

df = pd.read_csv('house_sales.csv')
df['city'] = df['city'].replace('--', np.nan).fillna('Unknown')
df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
df = df.dropna(subset=['sale_price'])
df['sale_price'] = df['sale_price'].astype(int)
df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce').fillna(pd.Timestamp('2023-01-01'))
mean_months = round(df['months_listed'].mean(), 1)
df['months_listed'] = df['months_listed'].fillna(mean_months).round(1)
df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
mean_bedrooms = round(df['bedrooms'].mean())
df['bedrooms'] = df['bedrooms'].fillna(mean_bedrooms).astype(int)

house_type_map = {
    'Det.': 'Detached', 'Detached': 'Detached',
    'Semi': 'Semi-detached', 'Semi-detached': 'Semi-detached',
    'Terr.': 'Terraced', 'Terraced': 'Terraced'
}
df['house_type'] = df['house_type'].map(house_type_map).fillna(df['house_type'])
df['house_type'] = df['house_type'].fillna(df['house_type'].mode()[0])
df['area'] = df['area'].astype(str).str.replace('sq.m.', '', regex=False).str.strip()
df['area'] = pd.to_numeric(df['area'], errors='coerce')
mean_area = round(df['area'].mean(), 1)
df['area'] = df['area'].fillna(mean_area).round(1)
clean_data = df.reset_index(drop=True)
clean_data.to_csv('clean_data.csv', index=False)

price_by_rooms = house_sales.groupby('bedrooms')['sale_price'].agg(
    avg_price='mean', var_price='var'
).reset_index()
price_by_rooms['avg_price'] = price_by_rooms['avg_price'].round(1)
price_by_rooms['var_price'] = price_by_rooms['var_price'].round(1)
print(price_by_rooms)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

train = pd.read_csv('train.csv')
validation = pd.read_csv('validation.csv')
features = ['city', 'months_listed', 'bedrooms', 'house_type', 'area']
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['city', 'house_type']),
    ('num', 'passthrough', ['months_listed', 'bedrooms', 'area'])
])

base_model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])
base_model.fit(train[features], train['sale_price'])
base_predictions = np.clip(base_model.predict(validation[features]), 0, None)
base_result = pd.DataFrame({'house_id': validation['house_id'], 'price': base_predictions})

compare_model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])
compare_model.fit(train[features], train['sale_price'])
compare_predictions = np.clip(compare_model.predict(validation[features]), 0, None)
compare_result = pd.DataFrame({'house_id': validation['house_id'], 'price': compare_predictions})

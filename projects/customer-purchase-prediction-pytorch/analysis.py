# Extracted from the original DataCamp/DataLab project workbook.
# Raw course-provided datasets are not redistributed in this public portfolio.

import pandas as pd
import numpy as np
import torch
import torch.nn as nn

# Cleaning
df = pd.read_csv('raw_customer_data.csv')
clean_data = df.copy()
clean_data['customer_id'] = clean_data['customer_id'].astype(int)
clean_data['time_spent'] = clean_data['time_spent'].fillna(clean_data['time_spent'].median())
mean_pages = clean_data['pages_viewed'].mean()
clean_data['pages_viewed'] = clean_data['pages_viewed'].fillna(mean_pages).round().astype(int)
clean_data['basket_value'] = clean_data['basket_value'].fillna(0)
clean_data['device_type'] = clean_data['device_type'].fillna('Unknown')
clean_data['customer_type'] = clean_data['customer_type'].fillna('New')
clean_data['purchase'] = clean_data['purchase'].astype(int)

# Feature preparation
df = pd.read_csv('model_data.csv')
model_feature_set = df.copy()
for col in ['time_spent', 'pages_viewed', 'basket_value']:
    min_val = model_feature_set[col].min()
    max_val = model_feature_set[col].max()
    model_feature_set[col] = (model_feature_set[col] - min_val) / (max_val - min_val)

model_feature_set = pd.get_dummies(
    model_feature_set,
    columns=['device_type', 'customer_type'],
    prefix=['device_type', 'customer_type'],
)
for col in model_feature_set.columns:
    if model_feature_set[col].dtype == bool:
        model_feature_set[col] = model_feature_set[col].astype(int)

# PyTorch model
torch.manual_seed(42)
train_df = pd.read_csv('input_model_features.csv')
val_df = pd.read_csv('validation_features.csv')
feature_cols = [
    'time_spent', 'pages_viewed', 'basket_value',
    'device_type_Desktop', 'device_type_Mobile', 'device_type_Tablet', 'device_type_Unknown',
    'customer_type_New', 'customer_type_Returning'
]
X_train = torch.tensor(train_df[feature_cols].values, dtype=torch.float32)
y_train = torch.tensor(train_df['purchase'].values, dtype=torch.float32).view(-1, 1)
X_val = torch.tensor(val_df[feature_cols].values, dtype=torch.float32)

class PurchaseNet(nn.Module):
    def __init__(self, n_features, n_hidden=8):
        super().__init__()
        self.hidden = nn.Linear(n_features, n_hidden)
        self.relu = nn.ReLU()
        self.output = nn.Linear(n_hidden, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return self.sigmoid(self.output(self.relu(self.hidden(x))))

purchase_model = PurchaseNet(n_features=X_train.shape[1], n_hidden=8)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(purchase_model.parameters(), lr=0.01)

purchase_model.train()
for epoch in range(300):
    optimizer.zero_grad()
    outputs = purchase_model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 50 == 0 or epoch == 299:
        acc = ((outputs > 0.5).float() == y_train).float().mean().item()
        print(f"epoch {epoch:4d} loss={loss.item():.4f} train_acc={acc:.4f}")

purchase_model.eval()
with torch.no_grad():
    val_probs = purchase_model(X_val)
    val_preds = (val_probs > 0.5).int().view(-1).tolist()

validation_predictions = pd.DataFrame({
    'customer_id': val_df['customer_id'].values,
    'purchase': val_preds,
})
print(validation_predictions.head(10))

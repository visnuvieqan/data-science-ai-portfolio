"""PyTorch neural network for customer purchase prediction."""
import torch
import torch.nn as nn
import pandas as pd

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

purchase_model.eval()
with torch.no_grad():
    val_preds = (purchase_model(X_val) > 0.5).int().view(-1).tolist()
validation_predictions = pd.DataFrame({
    'customer_id': val_df['customer_id'].values,
    'purchase': val_preds,
})
validation_predictions.to_csv('validation_predictions.csv', index=False)

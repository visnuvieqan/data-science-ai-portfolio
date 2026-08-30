# Customer Purchase Prediction with PyTorch

**Focus:** Neural networks, binary classification, preprocessing, and model inference.

This project predicts whether e-commerce customers will make a purchase from behavioral features such as session duration, pages viewed, basket value, device type, and customer type.

## Work performed
- Cleaned and transformed customer data with pandas and NumPy.
- Applied scaling and categorical encoding.
- Built a PyTorch neural network with a hidden layer, ReLU activation, sigmoid output, binary cross-entropy loss, and Adam optimization.
- Trained on the provided model dataset and generated predictions for an unseen validation set.

## Improvement notes
The original model showed a strong majority-class bias, so future iterations should emphasize confusion matrix, precision/recall/F1, ROC-AUC, class weighting, threshold tuning, and comparison with simpler baselines.

## Public repository files
- `analysis.py` — extracted analysis/source code from the original workbook
- `task3_pytorch_model.py` — standalone neural-network implementation
- `README.md` — project scope, methods, and highlights

> **Data note:** The original project used course-provided datasets in DataCamp/DataLab. Those raw datasets and reference images are intentionally not redistributed in this public repository. The source code keeps the original expected filenames for reproducibility with an authorized local copy of the data.

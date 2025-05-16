# %%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pickle
import sys
import xgboost as xgb
from dataprocessing import preprocess_dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# %%
DATA_DIR = "C:\\Users\\basel\\OneDrive\\Desktop\\Waterloo\\1 UNI\\4FYDP\\signecho\\ml\\data"
X, y = preprocess_dataset(DATA_DIR)

# %%
MODEL_DIR = "C:\\Users\\basel\\OneDrive\\Desktop\\Waterloo\\1 UNI\\4FYDP\\signecho\\ml\\model"
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Save the LabelEncoder
with open(f"{MODEL_DIR}\\label_encoder.pkl", "wb+") as f:
    pickle.dump(label_encoder, f)

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=20)

# %%
# Create the XGBoost model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')

# %%
# Train the model
model.fit(X_train, y_train)

# Save the XGBoost model
with open(f"{MODEL_DIR}\\xgb.pkl", "wb+") as f:
    pickle.dump(model, f)

# %%
# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"XGBoost Accuracy: {accuracy:.4f}")

# %%
# Create and train a Random Forest model
from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)
# Save the Random Forest model
with open(f"{MODEL_DIR}\\rf.pkl", "wb+") as f:
    pickle.dump(rf_model, f)

# Make predictions using Random Forest
rf_y_pred = rf_model.predict(X_test)

# Calculate accuracy for Random Forest
rf_accuracy = accuracy_score(y_test, rf_y_pred)
print(f"Random Forest Accuracy: {rf_accuracy:.4f}")


# %%
# Create and train a Support Vector Machine (SVM) model
from sklearn.svm import SVC

svm_model = SVC()
svm_model.fit(X_train, y_train)
# Save the SVM model
with open(f"{MODEL_DIR}\\svm.pkl", "wb+") as f:
    pickle.dump(svm_model, f)

# Make predictions using SVM
svm_y_pred = svm_model.predict(X_test)

# Calculate accuracy for SVM
svm_accuracy = accuracy_score(y_test, svm_y_pred)
print(f"SVM Accuracy: {svm_accuracy:.4f}")


# %%
# Create and train a K-Nearest Neighbors (KNN) model
from sklearn.neighbors import KNeighborsClassifier

knn_model = KNeighborsClassifier()
knn_model.fit(X_train, y_train)
# Save the KNN model
with open(f"{MODEL_DIR}\\knn.pkl", "wb+") as f:
    pickle.dump(knn_model, f)

# Make predictions using KNN
knn_y_pred = knn_model.predict(X_test)

# Calculate accuracy for KNN
knn_accuracy = accuracy_score(y_test, knn_y_pred)
print(f"KNN Accuracy: {knn_accuracy:.4f}")

# %%
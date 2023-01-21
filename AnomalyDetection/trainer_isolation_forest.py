import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np

# Load the data from a CSV file #빈칸은 nan으로
data = pd.read_csv('/content/drive/MyDrive/train.csv', na_values="nan")


# List of features to be used in the model
features = [
    'IP_source',
    'IP_destination',
    'l4_TCP_source_port',
    'l4_TCP_destination_port',
    'l4_TCP_flags_ACK',
    'source_identity',
    'destination_identity',
    'destination_labels_0',
    'destination_labels_1',
    'destination_labels_2',
    'destination_labels_3',
    'destination_labels_4',
    'Type',
    'traffic_direction',
    'trace_observation_point',
    'event_type_type',
    'Summary'
]

# Create a LabelEncoder object
le = LabelEncoder()

# Iterate through the features that need to be encoded
for feature in features:
    # Encode the feature values
    data[feature] = le.fit_transform(data[feature])

# Create a MinMaxScaler object
scaler = MinMaxScaler()

# Iterate through the features that need to be scaled
for feature in features:
    # Scale the feature values
    data[feature] = scaler.fit_transform(data[feature].values.reshape(-1,1))

# Create an Isolation Forest model
model = IsolationForest(random_state=0)

# Extract the feature values for the current row
feature_values = data[features].values

# Train the model on the current feature values
model.fit(feature_values)

# Save the model to a file
joblib.dump(model, "model_new.joblib")

# Saving the LabelEncoder object
joblib.dump(le, "le.joblib")

# Saving the MinMaxScaler object
joblib.dump(scaler, "scaler.joblib")

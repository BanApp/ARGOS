from pymongo import MongoClient
from pymongo.errors import PyMongoError
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

#모델 호출
model = joblib.load("model.joblib")

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

# Loading the LabelEncoder object
LabelE = joblib.load("le.joblib")

# Loading the MinMaxScaler object
 MinMaxSca = joblib.load("scaler.joblib")

# Create a LabelEncoder object
le = LabelE

# Create a MinMaxScaler object
scaler = MinMaxSca

# Set up change stream to listen for new insertions
while 1:
    try:
        change_stream = collection.watch()
        for change in change_stream:
            if change["operationType"] == "insert":
                new_data = change["fullDocument"]

                feature_values = [new_data.get(feature, "nan") for feature in features]

                # Encode the feature values with the appropriate labelEncoder
                for i in range(len(feature_values)):
                    feature_values[i] = le.transform([feature_values[i]])[0]

                # Scale the feature values with the appropriate MinMaxScaler
                for i in range(len(feature_values)):
                    feature_values[i] = scaler.transform([[feature_values[i]]])[0][0]

                # Reshape the new feature values into a 2D array with a single row
                feature_values = np.array(feature_values).reshape(1, -1)

                # Use the predict method to detect outliers
                prediction = model.predict(feature_values)

                # check the prediction, if it is -1, it means the new data is an outlier
                if prediction[0] == -1:
                    print("The new data is an outlier")
                else:
                    print("The new data is not an outlier")

    except PyMongoError as e:
        print(e)

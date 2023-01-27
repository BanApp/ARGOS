from pymongo import MongoClient
from pymongo.errors import PyMongoError
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import subprocess
import time
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]
anomaly_data = db["anomaly"]

features = ['IP_source', 'IP_destination', 'l4_TCP_source_port', 'l4_TCP_destination_port', 'l4_TCP_flags_ACK', 'source_identity', 'destination_identity',
            'Type','traffic_direction','trace_observation_point''event_type_type','Summary']

# 모델 호출
model = joblib.load("model_if.joblib")
encoder = joblib.load("encoder_if.joblib")

# Set up change stream to listen for new insertions
cnt = 1
normal = 1
anomaly = 0
df1 = pd.DataFrame(columns=features)
ck = 0
average = 0

while 1:
    try:
        change_stream = collection.watch()
        # 인코더 호출
        for change in change_stream:
            if change["operationType"] == "insert":
                new_data = change["fullDocument"]
                dt = new_data['time']
                new_data = pd.DataFrame(new_data, index=[0])
                new_data = new_data.reindex(columns=features, fill_value="nan")
                new_data = new_data.astype('str')
                if len(df1) < 7000:
                    df1 = df1.append(new_data, ignore_index=True)

                else:
                    if ck == 0:
                        normal = 1
                        anomaly = 0
                        ck = 1

                    if anomaly+normal >= 100:
                        print("=======================DONE!=======================")
                        print("AVR: ",(normal/(anomaly+normal)*100))
                        print()
                        normal = 1
                        anomaly = 0
                        average = 0
                    #print()

                # Encode the feature values with the appropriate labelEncoder
                try:
                    encoded_data = encoder.transform(new_data[features].values.reshape(-1, ).reshape(1, -1))
                    data = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(features))

                    # Use the predict method to detect outliers
                    prediction = model.predict(data)

                    # check the prediction, if it is -1, it means the new data is an outlier
                    if prediction[0] == -1:
                        print(datetime.now())
                        print(dt)
                        print(normal,anomaly)
                        print()
                        anomaly = anomaly + 1
                        df1 = df1.iloc[1:]
                        df1 = df1.append(new_data, ignore_index=True)
                        anomaly_data.insert_one(change["fullDocument"])
                        #print("The new data is an outlier")
                        train_data = pd.DataFrame(encoder.fit_transform(df1[features]))
                        model.fit(train_data)

                    else:
                        normal = normal + 1
                        #collection.delete_one({'_id': new_data['_id']})
                        #print("Good!")

                except:
                    print(datetime.now())
                    print(dt)
                    print(normal, anomaly)
                    print()
                    df1 = df1.iloc[1:]
                    df1 = df1.append(new_data, ignore_index=True)
                    anomaly_data.insert_one(change["fullDocument"])
                    anomaly = anomaly + 1
                    #print("The new data is an outlier")
                    train_data = pd.DataFrame(encoder.fit_transform(df1[features]))
                    model.fit(train_data)

    except PyMongoError as e:
        print(e)

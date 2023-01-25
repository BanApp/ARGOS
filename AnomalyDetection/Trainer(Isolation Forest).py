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

features = ['IP_source', 'IP_destination', 'l4_TCP_source_port', 'l4_TCP_destination_port', 'l4_TCP_flags_ACK', 'source_identity', 'destination_identity',
            'destination_labels_0','destination_labels_1','destination_labels_2','destination_labels_3','destination_labels_4',
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
while 1:
    try:
        change_stream = collection.watch()
        # 인코더 호출
        for change in change_stream: 
            if change["operationType"] == "insert":
                new_data = change["fullDocument"]
                new_data = pd.DataFrame(new_data, index=[0])
                new_data = new_data.reindex(columns=features, fill_value="nan")
                new_data = new_data.astype('str')
                if len(df1) < 10000:
                    df1 = df1.append(new_data, ignore_index=True)

                elif len(df1) >= 10000:
                    if ck == 0:
                        normal = 1
                        anomaly = 0
                        ck = 1

                    train_data = pd.DataFrame(encoder.fit_transform(df1[features]))
                    model.fit(train_data)

                    # Save the encoder
                    #joblib.dump(encoder,"encoder_if.joblib")
                    # Save the model
                    #joblib.dump(model,"model_if.joblib")

                    # 모델 호출
                    #model = joblib.load("model_if.joblib")
                    # 인코더 호출
                    #encoder = joblib.load("encoder_if.joblib")

                    df1 = df1.iloc[2:]
                    #print("normal: ",normal)
                    #print("anomaly: ",anomaly)
                    #print((normal/(anomaly+normal)*100))
                    cnt = cnt + 1

                    if anomaly+normal >= 1000:
                        print("=======================DONE!=======================")
                        print("AVR: ",(normal/(anomaly+normal)*100))
                        print()
                        normal = 1
                        anomaly = 0
                        cnt = 1
                    #print()

                # Encode the feature values with the appropriate labelEncoder
                try:
                    encoded_data = encoder.transform(new_data[features].values.reshape(-1, ).reshape(1, -1))
                    data = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(features))

                    # Use the predict method to detect outliers
                    prediction = model.predict(data)

                    # check the prediction, if it is -1, it means the new data is an outlier
                    if prediction[0] == -1:
                        anomaly = anomaly + 1
                        #print("The new data is an outlier")
                        #now = datetime.now()
                        #print(now)
                        #print()

                    else:
                        normal = normal + 1
                        #collection.delete_one({'_id': new_data['_id']})
                        #print("Good!")
                        #now = datetime.now()
                        #print(now)
                        #print()
                except:
                    anomaly = anomaly + 1
                    #print("The new data is an outlier")
                    #now = datetime.now()
                    #print(now)
                    #print()

    except PyMongoError as e:
        print(e)

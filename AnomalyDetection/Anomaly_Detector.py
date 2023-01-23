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

features = ['IP_source', 'IP_destination', 'l4_TCP_source_port', 'l4_TCP_destination_port', 'l4_TCP_flags_ACK', 'source_identity', 'destination_identity', 'traffic_direction', 'event_type_type']

# 모델 호출
model = joblib.load("model_if.joblib")
encoder = joblib.load("encoder_if.joblib")

# Set up change stream to listen for new insertions
cnt = 0
normal = 0
anomaly = 0
df1 = pd.DataFrame(columns=features)
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
                if len(df1) < 1000:
                    df1 = df1.append(new_data, ignore_index=True)

                elif len(df1) == 5000:
                    # len(df1): 사이클 마다 학습 시킬 데이터의 양
                    train_data = pd.DataFrame(encoder.fit_transform(df1[features]))
                    model.fit(train_data)

                    # Save the encoder
                    joblib.dump(encoder,"encoder_if.joblib")
                    # Save the model
                    joblib.dump(model,"model_if.joblib")

                    # 모델 호출
                    model = joblib.load("model_if.joblib")
                    # 인코더 호출
                    encoder = joblib.load("encoder_if.joblib")

                    df1 = df1.iloc[60:]
                    # df1.iloc[60:]: 앞에 60개를 지우겠다. 가중치 갱신
                    print("normal: ",normal)
                    print("anomaly: ",anomaly)
                    print("Result: ",anomaly/(normal+anomaly))
                    print()
                    normal = 0
                    anomaly = 0

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

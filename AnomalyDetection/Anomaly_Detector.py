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


# Connect to MongoDB
client = MongoClient("")
db = client[""]
collection = db[""]

features = ['IP_source', 'IP_destination', 'l4_TCP_source_port', 'l4_TCP_destination_port', 'l4_TCP_flags_ACK', 'source_identity', 'destination_identity', 'traffic_direction', 'event_type_type']


# Set up change stream to listen for new insertions

while 1:
    try:
        change_stream = collection.watch()
        # 모델 호출
        model = joblib.load("model_if.joblib")
        encoder = joblib.load("encoder_if.joblib")
        # 인코더 호출
        for change in change_stream:
            if change["operationType"] == "insert":
                new_data = change["fullDocument"]
                new_data = pd.DataFrame(new_data, index=[0])
                new_data = new_data.reindex(columns=features, fill_value='nan')

                # Encode the feature values with the appropriate labelEncoder
                try:
                    encoded_data = encoder.transform(new_data[features].values.reshape(-1,).reshape(1, -1))
                    data = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(features))

                    # Use the predict method to detect outliers
                    prediction = model.predict(data)

                    # check the prediction, if it is -1, it means the new data is an outlier
                    if prediction[0] == -1:
                        print("-1 The new data is an outlier")
                        now = datetime.now()
                        print(now)
                        print()
                    else:
                        #collection.delete_one({'_id': new_data['_id']})
                        print("Good!")
                        now = datetime.now()
                        print(now)
                        print()
                except:
                    pass
                    print("The new data is an outlier")
                    now = datetime.now()
                    print(now)
                    print()
                    t_encoded_data = encoder.fit_transform(new_data[features].values.reshape(-1,).reshape(1, -1))
                    train_data = pd.DataFrame(t_encoded_data, columns=encoder.get_feature_names_out(features))
                    model.fit(train_data)

                    # Save the encoder
                    joblib.dump(encoder, "encoder_if.joblib")
                    # Save the model
                    joblib.dump(model, "model_if.joblib")

                    # 모델 호출
                    model = joblib.load("model_if.joblib")
                    # 인코더 호출
                    encoder = joblib.load("encoder_if.joblib")
                   
    except PyMongoError as e:
        print(e)

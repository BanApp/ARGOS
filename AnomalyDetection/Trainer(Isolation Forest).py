import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import IsolationForest
import joblib

# 데이터 준비
df = pd.read_csv("/content/drive/MyDrive/train.csv")

features = ['IP_source', 'IP_destination', 'l4_TCP_source_port','l4_TCP_destination_port','l4_TCP_flags_ACK','source_identity','destination_identity','traffic_direction','event_type_type']

df[features] = df[features].astype('str')

import pandas as pd
from sklearn.preprocessing import OneHotEncoder

# Create an instance of OneHotEncoder
enc = OneHotEncoder(handle_unknown='ignore')

# Apply one-hot encoding to specified columns
one_hot_cols = pd.DataFrame(enc.fit_transform(df[['IP_source', 'IP_destination', 'l4_TCP_source_port','l4_TCP_destination_port','l4_TCP_flags_ACK','source_identity','destination_identity','traffic_direction','event_type_type']]).toarray())

# Add one-hot encoded columns to the original dataframe
df = pd.concat([df, one_hot_cols], axis=1)

# Drop the original columns
df.drop(['IP_source', 'IP_destination', 'l4_TCP_source_port','l4_TCP_destination_port','l4_TCP_flags_ACK','source_identity','destination_identity','traffic_direction','event_type_type'], axis=1, inplace=True)


# Create and train the model
model = IsolationForest(random_state=1)
model.fit(df)


# Save the encoder
joblib.dump(enc, "encoder_if.joblib")

#Save the model
joblib.dump(model, "model_if.joblib")

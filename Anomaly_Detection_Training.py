from pymongo import MongoClient
import numpy as np
import pandas as pd
from keras.layers import Input, Dense
from keras.models import Model
from sklearn.preprocessing import MinMaxScaler

# Connect to MongoDB
client = MongoClient("mongodb://username:password@host:port/")
db = client["logs"]
collection = db["network_flows"]

# Find all documents in the collection
data = list(collection.find())

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)

# Preprocess data
scaler = MinMaxScaler()
data = scaler.fit_transform(df)

# Define input and encoded layers
input_layer = Input(shape=(data.shape[1],))
encoded = Dense(64, activation='relu')(input_layer)
encoded = Dense(32, activation='relu')(encoded)

# Define decoded layers
decoded = Dense(64, activation='relu')(encoded)
decoded = Dense(data.shape[1], activation='sigmoid')(decoded)

# Create autoencoder model
autoencoder = Model(input_layer, decoded)

# Compile model
autoencoder.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

# Train model
autoencoder.fit(data, data, epochs=50, batch_size=32)

# Save model
autoencoder.save('autoencoder.h5')

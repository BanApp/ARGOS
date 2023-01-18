from keras.models import load_model
import numpy as np

# Load the trained model
autoencoder = load_model('autoencoder.h5')

# Preprocess new data in the same way as the training data
scaler = MinMaxScaler()
new_data = scaler.fit_transform(new_df)

# Use the model to predict the output for the new data
predictions = autoencoder.predict(new_data)

# Calculate the mean squared error between the predictions and the original data
mse = np.mean(np.power(new_data - predictions, 2), axis=1)

# Set a threshold for the mean squared error to define an anomaly
threshold = 0.05

# Find the data points that have a mean squared error greater than the threshold
anomalies = np.where(mse > threshold)

# Find the data points that have a mean squared error greater than the threshold
anomalies = np.where(mse > threshold)

# Print the anomalous data points IP, port, pod name and namespace
for index in anomalies[0]:
    print("Anomalous data point:")
    print("IP address:", new_df.iloc[index]["IP"]["source"])
    print("Port:", new_df.iloc[index]["l4"]["UDP"]["source_port"])
    print("Pod name:", new_df.iloc[index]["source"]["pod_name"])
    print("Namespace:", new_df.iloc[index]["source"]["namespace"])

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.preprocessing import LabelEncoder

data = pd.read_csv('/content/drive/MyDrive/train.csv')
data = data[:40000]
# Preprocessing

columns_to_encode = [
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

for column in columns_to_encode:
    data[column].fillna(0, inplace=True)

data = pd.get_dummies(data, columns=columns_to_encode)
    
# Scale data
scaler = MinMaxScaler()
data = scaler.fit_transform(data)

# Training
# Define encoder architecture
encoder = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(data.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu')
])

# Define decoder architecture
decoder = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(16,)),
    tf.keras.layers.Dense(data.shape[1], activation='sigmoid')
])

# Define autoencoder architecture
autoencoder = tf.keras.Sequential([encoder, decoder])

# Compile autoencoder
autoencoder.compile(optimizer='adam', loss='mean_squared_error')

# Train autoencoder
autoencoder.fit(data, data, epochs=20)

print("Train Done!")

autoencoder.save('/content/drive/MyDrive/anomaly/model.h5',save_format='h5')

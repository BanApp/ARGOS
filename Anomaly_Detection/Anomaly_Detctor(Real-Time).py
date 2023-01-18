from pymongo import MongoClient
from kafka import KafkaConsumer
import json
import tensorflow as tf
import pymongo

# Connect to MongoDB and fetch data from "network_flows" collection in "logs" database
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

# Define the autoencoder model
inputs = tf.keras.layers.Input(shape=(6,))
encoded = tf.keras.layers.Dense(32, activation='relu')(inputs)
decoded = tf.keras.layers.Dense(6, activation='sigmoid')(encoded)
autoencoder = tf.keras.Model(inputs, decoded)
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

# Set up Kafka consumer to consume data from a topic
consumer = KafkaConsumer('mytopic', bootstrap_servers='localhost:9092')

# Initialize empty list to store the last 100 data points for training
window = []

# Continuously train the model on incoming data and data fetched from
    while True:
        # Fetch the latest data from MongoDB
        cursor = collection.find().sort("_id", pymongo.DESCENDING).limit(100)
        data = list(cursor)
        data = [json.loads(d) for d in data]
        time = [d['flow']['time'] for d in data]
        verdict = [d['flow']['verdict'] for d in data]
        source = [d['flow']['IP']['source'] for d in data]
        destination = [d['flow']['IP']['destination'] for d in data]
        tcp_flags = [d['flow']['l4']['TCP']['flags'] for d in data]
        traffic_direction = [d['flow']['traffic_direction'] for d in data]
        df = pd.DataFrame({'time': time, 'verdict': verdict, 'source': source, 'destination': destination, 'tcp_flags': tcp_flags, 'traffic_direction': traffic_direction})
        x_train = df.values
        # Add the data to the training window
        window.extend(x_train)
        # Keep the window size fixed at 100
        window = window[-100:]
        autoencoder.fit(x_train, x_train, epochs=1, batch_size=len(x_train), verbose=0)

        # Remove the data that has been used for training from MongoDB
        collection.delete_many({'_id': {'$in': [d['_id'] for d in data]}})

        for msg in consumer:
            data = json.loads(msg.value)
            time = data['flow']['time']
            verdict = data['flow']['verdict']
            source = data['flow']['IP']['source']
            destination = data['flow']['IP']['destination']
            tcp_flags = data['flow']['l4']['TCP']['flags']
            traffic_direction = data['flow']['traffic_direction']
            new_data = [[time, verdict, source, destination, tcp_flags, traffic_direction]]
            new_data = np.asarray(new_data)
            # Use the trained model to make predictions on the new incoming data
            predictions = autoencoder.predict(new_data)
            # Compare the prediction error with a threshold to identify anomalies
            prediction_error = np.sum(np.square(new_data - predictions))
            if prediction_error > threshold:
                print("Anomaly detected:", data)
                
                # Add the anomalous data to MongoDB
                #collection.insert_one(data)
            else:
                print("Normal data:", data)

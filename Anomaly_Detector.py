from pymongo import MongoClient
from kafka import KafkaProducer
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import numpy as np
from keras.models import load_model

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['logs']
collection = db['network_flows']

# Connect to Kafka
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Continuously read data from MongoDB and stream it to Kafka
while True:
    cursor = collection.find({}, {'_id': 0})
    for document in cursor:
        # Convert the document to a JSON string
        data = json.loads(json.dumps(document))
        # Extract the necessary information from the JSON object
        IP = data["flow"]["IP"]["source"]
        Port = data["flow"]["l4"]["UDP"]["destination_port"]
        Pod_name = data["flow"]["source"]["pod_name"]
        Namespace = data["flow"]["source"]["namespace"]
        # Create a new dictionary with the extracted information
        new_data = {"IP": IP, "Port": Port, "Pod_name": Pod_name, "Namespace": Namespace}
        # Convert the new dictionary to a JSON string
        data = json.dumps(new_data)
        # Send the data to the "network_flows" topic in Kafka
        producer.send('network_flows', value=data)
        

# Create a Spark Streaming context with a batch interval of 1 second
sc = SparkContext("local[*]", "AnomalyDetection")
ssc = StreamingContext(sc, 1)

# Create a Kafka stream using the KafkaUtils.createStream method
kafkaStream = KafkaUtils.createStream(ssc, "localhost:2181", "anomaly_detection_group", {"network_flows": 1})

# Load the pre-trained autoencoder model
autoencoder = load_model("autoencoder.h5")

# Define a function to preprocess the data and detect anomalies
def detect_anomalies(rdd):
    # Convert the RDD to a DataFrame
    data = sqlContext.read.json(rdd)

    # Extract the necessary columns
    data = data.select(["IP", "Port", "Pod_name", "Namespace", "flow.l4.UDP.destination_port"])

    # Convert the DataFrame to a Numpy array
    data = data.toPandas().values

    # Preprocess the data
    data = data.astype(float)
    data = np.nan_to_num(data)

    # Use the autoencoder to detect anomalies
    predictions = autoencoder.predict(data)
    mse = np.mean(np.power(data - predictions, 2), axis=1)

    # Set a threshold for the mean squared error to define an anomaly
    threshold = 3
    anomalies = np.where(mse > threshold)
    if len(anomalies[0]) > 0:
        print("Anomaly detected!")

    # Print the anomalous data points IP, port, pod name and namespace
    for index in anomalies[0]:
        print("Anomalous data point:")
        print("IP address:", data.iloc[index]["IP"])
        print("Port:", data.iloc[index]["Port"])
       

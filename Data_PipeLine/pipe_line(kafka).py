from pymongo import MongoClient
from kafka_python import KafkaProducer
from kafka_python import KafkaConsumer

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

# Set up change stream to listen for new insertions
cursor = collection.watch()

# Set up a Kafka producer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Continuously listen for new documents and send them to Kafka
for change in cursor:
    if change["operationType"] == "insert":
        new_doc = change["fullDocument"]
        producer.send('new_network_flows', new_doc)

# Create a Kafka consumer to listen for messages on the "new_network_flows" topic
consumer = KafkaConsumer('new_network_flows', bootstrap_servers='localhost:9092')

# Continuously poll for new messages and print them out
for message in consumer:
    print(message.value)

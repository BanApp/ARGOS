from pymongo import MongoClient
from pymongo.errors import PyMongoError
#from kafka import KafkaProducer

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

# Set up Kafka producer
#producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Set up change stream to listen for new insertions
while 1:
    try:
        change_stream = collection.watch()
        for change in change_stream:
            print(change)
            #if change["operationType"] == "insert":
                #new_data = change["fullDocument"]
                ## Print new data
                #print(new_data)
                # Send data to Kafka topic
                #producer.send("network_flows:", new_data)

    except PyMongoError as e:
        print(e)
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

# Set up change stream to listen for new insertions
while 1:
    try:
        change_stream = collection.watch()
        for change in change_stream:
            if change["operationType"] == "insert":
                new_data = change["fullDocument"]
                print(new_data)

    except PyMongoError as e:
        print(e)

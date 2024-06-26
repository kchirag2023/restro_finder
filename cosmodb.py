import os
import pymongo
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.restro

# Define the collection
collection = db.restaurants

# JSON data from file
json_file = "/Users/kumarchirag/Desktop/microsoft_project/db.json"

with open(json_file, 'r') as f:
    data = json.load(f)

# Insert data into MongoDB
result = collection.insert_many(data)

# Print result
print(f"Inserted {len(result.inserted_ids)} documents.")

# Close MongoDB connection
client.close()


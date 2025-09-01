from pymongo import MongoClient
import pprint

client = MongoClient("mongodb://localhost:27017/")
db = client["oantracker"]
collection = db["expense"]

# Fetch a sample document
sample = collection.find_one()
pprint.pprint(sample)
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# List all databases
print("Databases:")
for db_name in client.list_database_names():
    print(f" - {db_name}")

# Optional: list collections in a specific database
db = client["oantracker"]  
print("\nCollections in that database:")
for coll_name in db.list_collection_names():
    print(f" - {coll_name}")
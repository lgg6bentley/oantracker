from pymongo import MongoClient
from datetime import datetime
from dateutil import parser

# 🔗 Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["oantracker"]
collection = db["expense"]

# 🧼 Define ghost date threshold
ghost_date = datetime(1970, 1, 2)

# 🗑️ 1. Remove documents with missing or null 'date'
result_null = collection.delete_many({
    "$or": [
        {"date": {"$exists": False}},
        {"date": None}
    ]
})
print(f"Deleted {result_null.deleted_count} documents with missing/null date.")

# 🔍 2. Preview and delete ghost documents with datetime type
ghosts = collection.find({"date": {"$lt": ghost_date}})
for ghost in ghosts:
    print("Ghost (datetime) found:", ghost)
result_ghost = collection.delete_many({"date": {"$lt": ghost_date}})
print(f"Deleted {result_ghost.deleted_count} documents with ghost dates before {ghost_date.date()}.")

# 🗑️ 3. Remove ghost documents with string-based dates
string_ghosts = []
for doc in collection.find({"date": {"$type": "string"}}):
    try:
        parsed = parser.parse(doc["date"])
        if parsed < ghost_date:
            string_ghosts.append(doc["_id"])
            print("Ghost (string) found:", doc)
    except Exception as e:
        print("Unparsable date:", doc["date"])

if string_ghosts:
    result_string_ghost = collection.delete_many({"_id": {"$in": string_ghosts}})
    print(f"Deleted {result_string_ghost.deleted_count} string-based ghost documents.")
else:
    print("No string-based ghost documents found.")
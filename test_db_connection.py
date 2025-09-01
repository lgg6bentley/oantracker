from pymongo import MongoClient

# Paste your FULL connection string here
client = MongoClient("mongodb+srv://lgg6bentley_db_user:YOUR_PASSWORD@cluster0.duymf0y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Connection Successful! Your connection string is correct.")
except Exception as e:
    print("Connection Failed! Double-check your username, password, and connection string.")
    print(f"Error: {e}")
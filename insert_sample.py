from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["oantracker"]
collection = db["expense"]

sample_receipt = {
    "user_id": "bentley001",
    "date": "2025-09-01",
    "merchant": "Tim Hortons",
    "category": "Food & Beverage",
    "amount": 6.25,
    "currency": "CAD",
    "payment_method": "Credit Card",
    "items": [
        {"name": "Coffee", "quantity": 1, "price": 2.25},
        {"name": "Bagel", "quantity": 1, "price": 4.00}
    ],
    "receipt_image": "",
    "notes": "Breakfast before work"
}

collection.insert_one(sample_receipt)
print("Sample receipt inserted.")
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.payment_links  
users_collection = db.users
payments_collection = db.payments


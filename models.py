from pymongo import MongoClient

client = MongoClient("mongodb+srv://tombrain1011:icdO8YDs9E8HOoBJ@cluster0.uso4lqs.mongodb.net/Emily?retryWrites=true&w=majority&appName=Cluster0")
db = client.payment_links  
users_collection = db.users
payments_collection = db.payments


from pymongo import MongoClient

uri = "mongodb+srv://abdullah:abdullah@cluster0.s1kvb8r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

db = client.fyp_blender_db

users_collection = db["users_collection"]
functions_collection = db["functions_collection"]


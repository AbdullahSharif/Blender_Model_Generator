from pymongo import MongoClient

import os

uri = os.getenv("MONGO_DB_URL")

client = MongoClient(uri)

db = client.fyp_blender_db

users_collection = db["users_collection"]
functions_collection = db["functions_collection"]


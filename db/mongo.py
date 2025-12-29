from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set")

client = MongoClient(MONGO_URI)
db = client["cookit"]
recipes = db["recipes"]

def save_recipe(data: dict):
    recipes.insert_one(data)

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

from bson import ObjectId

def get_recipes(limit=20):
    return list(
        recipes.find({}, {
            "title": 1,
            "original_url": 1
        }).limit(limit)
    )

def get_recipe_by_id(recipe_id: str):
    return recipes.find_one({"_id": ObjectId(recipe_id)})


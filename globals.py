from pymongo import MongoClient

secret_key = "dev-only-7f2c9a1e4b6d8f0a3c5e7b9d1f4a6c8e"

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB

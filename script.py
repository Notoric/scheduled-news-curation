import time
import json
import pymongo
import requests
from datetime import datetime, timedelta

print("   _____ _   _  _____ ")
print("  / ____| \ | |/ ____|")
print(" | (___ |  \| | |")
print("  \___ \|     | |")
print("  ____) | |\  | |____")
print(" |_____/|_| \_|\_____|")

# Load config
print("Loading config...")

with open('config.json') as f:
    config = json.load(f)

print("Config loaded!")

mongo_url = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}/"
mongo_db = config['mongo']['db']

# Connect to MongoDB
print("Connecting to MongoDB...")

client = pymongo.MongoClient(mongo_url)
db = client[mongo_db]

print("Connected to MongoDB!")

# Create collections if they dont exist
def create_collections():
    collections = ['weather', 'newsfeed']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"Created collection {collection}")

# Get weather data

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={config['weather']['city']}&appid={config['weather']['api_key']}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

create_collections()


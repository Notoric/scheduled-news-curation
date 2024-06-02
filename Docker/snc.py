import time
import os
import json
import pymongo
import requests
import schedule
from groq import Groq
from datetime import datetime, timedelta

print("   _____ _   _  _____ ")
print("  / ____| \ | |/ ____|")
print(" | (___ |  \| | |")
print("  \___ \|     | |")
print("  ____) | |\  | |____")
print(" |_____/|_| \_|\_____|")

# Load config
print("Loading config...")

if os.path.exists('config.json') == False:
    print("Config file not found, Creating...")
    exec(open('generate-config.py').read())

with open('config.json') as f:
    config = json.load(f)

print("Config loaded!")

mongo_url = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}/"
mongo_db = config['mongo']['db']

weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={config['weather']['city']}&appid={config['weather']['api_key']}&units=metric"

news_url = f"http://newsapi.org/v2/top-headlines?country={config['news']['country']}&apiKey={config['news']['api_key']}"

groq_key = config['groq']['api_key']

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
    print("Getting weather data...")

    response = requests.get(weather_url)
    data = response.json()

    response = {}

    response['location'] = data['name']
    temp = data['main']['temp']
    temp = round(temp * 2 + 0.5) / 2
    response['temperature'] = str(temp) + "°C"
    response['humidity'] = str(data['main']['humidity']) + "%"
    response['status'] = data['weather'][0]['description'].capitalize()
    windspeed = data['wind']['speed']

    if windspeed < 2:
        response['wind'] = "Calm"
    elif windspeed < 5:
        response['wind'] = "Light Breeze"
    elif windspeed < 11:
        response['wind'] = "Gentle breeze"
    elif windspeed < 17:
        response['wind'] = "Moderate breeze"
    elif windspeed < 23:
        response['wind'] = "Strong breeze"
    elif windspeed < 30:
        response['wind'] = "High winds"
    elif windspeed < 49:
        response['wind'] = "Gale force winds"
    else:
        response['wind'] = "Storm"
    
    if data['visibility'] < 6000:
        response['fog'] = "true"

    response['icon'] = f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"

    print("Weather data retrieved!")
    return response

# Write weather data to MongoDB

def write_weather():
    print("Writing weather data to MongoDB...")

    weather = get_weather()
    weather['timestamp'] = datetime.now()

    db.weather.replace_one({}, weather, upsert=True)

    print("Weather data written to MongoDB!")

# Get newsfeed data

def get_newsfeed(category='general'):
    print(f"Getting {category} newsfeed data...")

    url = news_url + f"&category={category}"

    response = requests.get(url)
    data = response.json()

    articles = []

    for article in data['articles']:
        article_data = {}
        article_data['title'] = article['title']
        article_data['url'] = article['url']
        article_data['author'] = article['author']
        article_data['category'] = category
        article_data['timestamp'] = datetime.now()
        articles.append(article_data)

    print("Newsfeed data retrieved!")
    return articles

# Get most interesting news articles with AI

def get_interesting_news(articles):
    print("Getting interesting news...")
    interesting_articles = []

    try:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model="gemma-7b-it",
            messages=[
                {
                    "role": "system",
                    "content": "You will be given an array of json elements, please provide the 3 indexes of the most interesting, important and notable news headlines that a mid-twenties person would like to read in the following format: {\"most_interesting\": {\"index\": index,\"title\": title},\"second_most_interesting\": {\"index\": index,\"title\": title},\"third_most_interesting\": {\"index\": index,\"title\": title}}"
                },
                {
                    "role": "user",
                    "content": str(articles)
                }
            ],
            temperature=1.3,
            max_tokens=1024,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )

        response = str(completion.choices[0].message.content)
        response = response.replace("\n", " ")
        response = json.loads(response)
    except Exception as e: # If ai doesnt return a valid response, check anyway, if not use the first 3 articles
        try:
            response = e
            response = response[18:]
            response = json.loads(response)
            response = response['error']['failed_generation']
            response = response.replace("\n", " ")
            response = json.loads(response)
        except:
            print("Error selecting articles! Using random selection...")
            response = {
                "most_interesting": {
                    "index": 0,
                    "title": "Interesting"
                },
                "second_most_interesting": {
                    "index": 1,
                    "title": "Interesting"
                },
                "third_most_interesting": {
                    "index": 2,
                    "title": "Interesting"
                }
            }

    selected_articles = []

    article_index = [0, 1, 2]
    try:
        article_index[0] = response['most_interesting']['index']
        article_index[1] = response['second_most_interesting']['index']
        article_index[2] = response['third_most_interesting']['index']
        print("Selected articles:" + str(article_index))
    except Exception as e:
        print(e)
        article_index = [0, 1, 2]
        print("Using default article selection...")


    for i in article_index:
        article = articles[i]
        selected_article = {}
        selected_article['title'] = article['title']
        selected_article['author'] = article['author']
        selected_article['url'] = article['url']
        selected_article['category'] = article['category']
        selected_article['timestamp'] = datetime.now()
        selected_articles.append(selected_article)

    print("Interesting news retrieved!")

    return selected_articles

# Write newsfeed data to MongoDB

def write_newsfeed(articles):
    print("Writing newsfeed data to MongoDB...")

    for article in articles:
        db.newsfeed.replace_one({'url': article['url']}, article, upsert=True)

    print("Newsfeed data written to MongoDB!")

# Get articles from all newsfeeds

def get_all_news():
    print("Getting all news articles...")

    write_newsfeed(get_interesting_news(get_newsfeed("technology")))
    write_newsfeed(get_interesting_news(get_newsfeed("science")))
    
# Delete all old news articles

def delete_old_news():
    print("Deleting old news articles...")

    hrs = int(config['news']['article_lifetime'])

    db.newsfeed.delete_many({'timestamp': {'$lt': datetime.now() - timedelta(hours=1) }})

    print("Old news articles deleted!")

# Main script

create_collections()

schedule.every(5).minutes.do(write_weather)
schedule.every(int(config['news']['article_interval'])).hours.do(get_all_news)
schedule.every(1).hours.do(delete_old_news)

write_weather()
get_all_news()
delete_old_news()

while True:
    schedule.run_pending()
    time.sleep(1)
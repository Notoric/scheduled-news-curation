import os
import json

# Load the template
with open('config_template.json', 'r') as template_file:
    config_template = template_file.read()

# Replace the placeholders with the actual values
config = config_template.replace('$MONGO_HOST', os.environ['MONGO_HOST']) \
    .replace('$MONGO_PORT', os.environ['MONGO_PORT']) \
    .replace('$MONGO_DB', os.environ['MONGO_DB']) \
    .replace('$GROQ_API_KEY', os.environ['GROQ_API_KEY']) \
    .replace('$OPENWEATHERMAP_API_KEY', os.environ['OPENWEATHERMAP_API_KEY']) \
    .replace('$OPENWEATHERMAP_CITY', os.environ['OPENWEATHERMAP_CITY']) \
    .replace('$NEWSAPI_API_KEY', os.environ['NEWSAPI_API_KEY']) \
    .replace('$NEWSAPI_COUNTRY', os.environ['NEWSAPI_COUNTRY']) \
    .replace('$NEWSAPI_ARTICLE_LIFETIME', os.environ['ARTICLE_LIFETIME']) \
    .replace('$NEWSAPI_ARTICLE_INTERVAL', os.environ['ARTICLE_INTERVAL'])

# Write the config to a file
with open('config.json', 'w') as config_file:
    config_file.write(config)

print("Config file created!")
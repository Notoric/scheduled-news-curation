# Scheduled News Curation
This is a python script which leverages the python schedule library to populate a mongo database with automatically expiring news and weather. Each article is allowed a lifetime in hours as defined in the config, and 9 new articles from 3 different categories are gotten every few hours, as defined in the config. Weather is gotten and updated every 5 minutes.
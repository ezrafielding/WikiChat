import wordprep, chatmodel, twitterhelp
import tensorflow as tf
import numpy as np
import nltk
import os.path
import tweepy
import sqlite3
import time
import json
import argparse

# Argument Parsing
parser = argparse.ArgumentParser(description="WikiChat is a retrieval based Twitter direct message chatbot written in Python 3.8.10. WikiChat can answer questions with informaiton from Wikipedia (hence the name).")
parser.add_argument("--consumer_key", help="Consumer Twitter API key", required=True)
parser.add_argument("--consumer_secret", help="Consumer Twitter API secret", required=True)
parser.add_argument("--access_token", help="Twitter API Access Token", required=True)
parser.add_argument("--access_token_secret", help="Twitter API Access Token secret", required=True)
parser.add_argument("--user_id", help="Twitter User ID", required=True)
parser.add_argument("--weather_api", help="OpenWeatherMap API key", required=True)
args = parser.parse_args()

# Twitter API information
consumer_key = args.consumer_key
consumer_secret = args.consumer_secret
access_token = args.access_token
access_token_secret = args.access_token_secret
twitter_user_ID = args.user_id

# Open Weather Map API information
weather_api = args.weather_api

# Wait time between DM fetch calls
dm_fetch_wait_time = 90

# Intent and Database relative file locations
intents_file_loaction = 'data/intents/intents.json'
db_file_location = 'data/db/messages.sql'

def openDB():
    '''Creates or opens the DM database.

    Args:

    Returns:
        The open database and a database cursor object.
    '''
    # Checks if database currently exists
    if os.path.exists(db_file_location):
        # Connects to database and creates cursor object
        database = sqlite3.connect(db_file_location)
        dbcursor = database.cursor()
    else:
        # Creates the database
        database = sqlite3.connect(db_file_location)
        database.execute('''CREATE TABLE DIRECTMESSAGE
                        (ID INTEGER(20) NOT NULL,
                        SENDER_ID INTEGER(20) NOT NULL,
                        RECIPIENT_ID INTEGER(20) NOT NULL,
                        TEXT VARCHAR(255),
                        PRIMARY KEY(ID));''')
        # Creates cursor object
        dbcursor = database.cursor()

    return database, dbcursor

def main():
    # Opens intents.json file
    with open(intents_file_loaction) as file:
        intents_file = json.load(file)

    try:
        # Collects known words, intents and intent/pattern pairs from intents.json
        words, intents, intent_pairs = wordprep.get_intent_data(intents_file)
    except:
        nltk.download('punkt')
        words, intents, intent_pairs = wordprep.get_intent_data(intents_file)
    # Creates or loads intent prediction model
    intent_model = chatmodel.model_prep(words, intents, intent_pairs)

    # Creates or opens the DM database
    print("Loading Database...")
    database, dbcursor = openDB()
    print("Database load complete!")

    # Authenticates Twitter and connects to the API
    print("Connecting Twitter API...")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    print("Twitter API connection complete!\n")

    while True:
        # Fetches list of Direct messages from twitter
        print("Fetching Direct Messages...")
        messages = api.list_direct_messages()
        # Determines which messages are new
        new_messages = twitterhelp.get_new_mesages(messages, dbcursor, twitter_user_ID)
        # Responds to new messages if there are any
        if len(new_messages) != 0:
            twitterhelp.respond_to_messages(api, dbcursor, new_messages, intent_model, intents_file, intents, words)
        # Database changes are committed
        database.commit()
        # A wait is introduced to avoid exceeding twitter api limits
        time.sleep(dm_fetch_wait_time)

if __name__ == "__main__":
    main()
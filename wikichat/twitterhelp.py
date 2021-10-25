import wordprep, qsearch
import numpy as np
import time

# SQL command for adding new messages to database
addEntreStr = '''INSERT INTO DIRECTMESSAGE(ID, SENDER_ID, RECIPIENT_ID, TEXT) 
                VALUES(?, ?, ?, ?)'''

def send_message(intent, intents_file, api, text, recipient):
    """Responds to a message based on its intent tag.

    Args:
        intent: Contains the intent of the current message.
        intents_file: intents.json file.
        api: Tweepy twitter api object.
        text: Text of the message.
        recipient: Twitter User ID of the user the resposne needs to be sent to.

    Returns:
        A Direct Message Object of the recently sent response.
    """
    # Prints out intent of current message for easy debug
    print("Message intent: ", intent[0])
    # Trys the following. Returns "I do not understand" message if exception is thrown
    try:
        # Checks for intent type
        if intent[0] == "wiki":
            # Queries Wikipedia
            ans, url = qsearch.wiki_search(text)
            response = ans + ". " + url
        elif intent[0] == "time":
            # Returns the current time
            t = time.localtime()
            response = wordprep.return_response(intents_file, intent[0]).format(t=time.strftime("%H:%M", t))
        elif intent[0] == "location":
            # Returns the user's location if available
            response = qsearch.location_search(api, wordprep.return_response(intents_file, intent[0]), recipient)
        elif intent[0] == "weather":
            # Queries the current weather conditions
            response = qsearch.weather_search(api, recipient)
        else:
            # Returns a random generic response
            response = wordprep.return_response(intents_file, intent[0])
    except:
        # Returns a "noanswer" response
        response = wordprep.return_response(intents_file, 'noanswer')

    # Sends generated or generic response to recipient
    sent_message = api.send_direct_message(recipient, response)
    return sent_message

def get_new_mesages(messages, dbcursor, twitter_user_ID):
    """Looks for and returns new messages from DM list.

    Args:
        messages: List of all direct messages.
        dbcursor: Cursor object to write to and read from database.
        twitter_user_ID: The user ID of the api linked twitter account.

    Returns:
        a list of new messages.
    """
    new_messages = []
    # Iterates through all messages in list from twitter api
    for message in messages:
        # Checks if message is from the bot or not
        if str(message.message_create['sender_id']) != twitter_user_ID:
            # Checks if message already exists in database
            dbcursor.execute("SELECT * FROM DIRECTMESSAGE WHERE ID = ?;", (str(message.id),))
            existQuery = dbcursor.fetchone()
            # Checks if anything is returned in the query
            if existQuery is not None:
                print('No new DMs\n-------------------')
                # Breaks after old DM is found
                break
            else:
                print('New DM recieved!')
                # Adds new DM to database
                dbcursor.execute(addEntreStr, (message.id, message.message_create['sender_id'], message.message_create['target']['recipient_id'], message.message_create['message_data']['text']))
                print("Message ID: ", message.id)
                print("Text: ", message.message_create['message_data']['text'],'\n+++++++++++++++++++')
                # New message appended to new message list
                new_messages.append(message)

    return new_messages

def respond_to_messages(api, dbcursor, new_messages, intent_model, intents_file, intents, words):
    """Responds to list of new messages based on intent.

    Args:
        api: Tweepy twitter api object.
        dbcursor: Cursor object to write to and read from database.
        new_messages: List of new messages.
        intent_model: Model for intent prediction.
        intents_file: intents.json file.
        intents: List of all available intents.
        words: List of all know words.

    Returns:
        .
    """
    # Iterates through new messages
    for nmessage in reversed(new_messages):
        # Stores recepient of the response to be sent
        recipient = nmessage.message_create['sender_id']
        print("Responding to: ", recipient)
        # Stores text of recieved message
        text = str(nmessage.message_create['message_data']['text'])
        # Converts text to a word bag for model prediction
        dm_word_bag = np.array([wordprep.build_bag(text, words)])
        # Intent is predicted and intent is stored
        results = intent_model.predict(dm_word_bag)
        results = list(results[0])
        intent = (intents[results.index(max(results))], results.index(max(results)))
        # New message is sent based on intent
        sent_message = send_message(intent, intents_file, api, text, recipient)
        print('-')
        # New Message is added to the database
        dbcursor.execute(addEntreStr, (sent_message.id, sent_message.message_create['sender_id'], sent_message.message_create['target']['recipient_id'], sent_message.message_create['message_data']['text']))
    print('-------------------')

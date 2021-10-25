from googlesearch import search
import requests
import main

# Weather API key, url and default city for search
weather_api_key = main.weather_api
weather_url = 'https://api.openweathermap.org/data/2.5/weather?'
weather_default_city = 'Cape Town'

def wiki_search(question):
    """Sends a question to google and queries wikipedia with the results.

    Args:
        question: String containing the question sent by the user.

    Returns:
        String containing Wikipedia page summary and url.
    """
    # Iterates through google search results for wiki pedia articals
    for result in search(question+ " 'wikipedia", tld='co.za', lang='en', num=1, stop=1):
        # Gets wikipedia page name
        page_name = result.split("/")[-1]
        # Wikipedia api request for page json
        page = requests.get("http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext=1&titles="+page_name).json()
        # Gets wikipedia page id
        page_id = list(page['query']['pages'].keys())[0]

    return page['query']['pages'][page_id]['extract'].split(". ")[0], result

def location_search(api, response_pattern, user_id):
    """Fetches user location from Twitter.

    Args:
        api: Tweepy Twitter api object.
        response_pattern: The string of the response which the location will be embeded in.
        user_id: The twitter user id of the user for the location search

    Returns:
        String containing users location.
    """
    # User location from twitter api
    loc = api.get_user(str(user_id)).location
    # Checks if location is empty or not
    if len(loc) > 0:
        # Embeds user location in response pattern
        return response_pattern.format(loc=loc)
    else:
        return "I can't find your location"

def weather_search(api, user_id):
    """Contact openweather api for current weather.

    Args:
        api: Tweepy Twitter api object.
        user_id: The twitter user id of the user for the location search

    Returns:
        Current weather conditions.
    """
    # Fetches current user location from twitter
    weather_city = api.get_user(str(user_id)).location
    # Constructs url query
    url_query = weather_url+"q="+weather_city+"&units=metric&appid="+weather_api_key
    # URL request made
    weather_response = requests.get(url_query)
    response = ''
    # Checks if successful response recieved
    if weather_response.status_code != 200:
        # Sets city for weather query to default
        weather_city = weather_default_city
        response += "Could not find a valid location for you on Twitter. Here is the weather for "+weather_city+" instead.\n"
        # Constructs an makes new url query with default city
        url_query = weather_url+"q="+weather_city+"&units=metric&appid="+weather_api_key
        weather_response = requests.get(url_query)

    # Converts weather data to json
    weather_data = weather_response.json()
    # Formats output
    response += "Weather in "+weather_city+":\nCondition: "+weather_data['weather'][0]['description']
    response += "\nThe temperature is "+ str(weather_data['main']['temp']) + " degrees celsius"
    
    return response
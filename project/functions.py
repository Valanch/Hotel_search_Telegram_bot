import datetime
import os

import requests
from dotenv import load_dotenv

from history import history
from loader import bot

load_dotenv()
hotel_API_KEY = os.getenv("hotels_API_KEY")


def log(message, command, city, hotels):

    # Logs the user queries based on their telegram id
    if message.from_user.id not in history.log:
        history.log[message.from_user.id] = dict()
    history.log[message.from_user.id][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = [command, city, hotels]


def hotel_request(message):

    # Sends a request to hotel API using the personal parameters from history.data
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": history.data[message.from_user.id]["city"]}
    headers = {
        "X-RapidAPI-Key": hotel_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    location_id = data["sr"][0]['gaiaId']
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": location_id},
        "checkInDate": {
            "day": 10,
            "month": 6,
            "year": 2023
        },
        "checkOutDate": {
            "day": 15,
            "month": 6,
            "year": 2023
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": history.data[message.from_user.id]["number"],
        "sort": history.data[message.from_user.id]["sort"],
        "filters": {"price": {
            "max": history.data[message.from_user.id]["maxprice"],
            "min": history.data[message.from_user.id]["minprice"]
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": hotel_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    hotel_data = response.json()
    hotel_data = hotel_data.get("data").get("propertySearch").get("properties")

    return hotel_data


def hotel_compute(data):

    # Makes a dictionary of hotel names and their ids for fetching the photos
    hotels = dict()

    for cur_hotel in data:
        hotels[cur_hotel.get('name')] = get_pictures(cur_hotel.get("id"))
        # hotel['price'] = hotel_price(cur_hotel)

    return hotels


def get_pictures(hotel_id):

    # Requests hotel pictures through hotels api
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "046ce92f3fmsh1f3fee9b942b3d9p123f1bjsn8e796bb748da",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    hotel_data = response.json()
    hotel_data = hotel_data.get("data").get("propertyInfo").get("propertyGallery").get("images")
    hotel_pics = []

    for count in range(3):
        pic = hotel_data[count].get("image").get("url")
        hotel_pics.append(pic)

    return hotel_pics


def fetch_city(message):

    # Gets the city from message, puts it in history.data, goes to get number of hotels for lowprice and highprice,
    # goes to fetch the price range for bestdeal command
    try:
        city = message.text.strip()
        history.data[message.from_user.id]["city"] = city
        if history.data[message.from_user.id]["command"] == "bestdeal":
            bot.send_message(message.from_user.id,
                             "Enter the price range in usd, using space in between.\nExample: 100 400")
            bot.register_next_step_handler(message, bestdeal_price_range)
        else:
            bot.send_message(message.from_user.id, "How many hotels? 1-5")
            bot.register_next_step_handler(message, fetch_hotel_num)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over or refer to /help command.")


def fetch_hotel_num(message):

    # Gets the number of hotels, stores it in history.data, forwards to photo check
    try:
        hotel_num = int(message.text)
        if hotel_num < 1 or hotel_num > 5:
            bot.send_message(message.from_user.id, "Wrong number of hotels. Start over or refer to /help command")
        else:
            history.data[message.from_user.id]["number"] = hotel_num
            bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
            bot.register_next_step_handler(message, photo_check)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over or refer to /help command.")

def bestdeal_price_range(message):

    # Allows manual entry for price range if the chosen command is bestdeal. Forwards to the usual loop.
    data = message.text.split()
    try:
        history.data[message.from_user.id]["maxprice"] = int(data[1])
        history.data[message.from_user.id]["minprice"] = int(data[0])
        bot.send_message(message.from_user.id, "How many hotels? 1-5")
        bot.register_next_step_handler(message, fetch_hotel_num)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over or refer to /help command.")


def photo_check(message):

    # Checks if photos need to be posted. If True, then requests the number, if False - goes straight to results.
    if message.text.lower() == "yes":
        history.data[message.from_user.id]["photo_check"] = 1
        bot.send_message(message.from_user.id, "How many pictures per hotel? 1-3")
        bot.register_next_step_handler(message, photo_num)
    elif message.text.lower() == "no":
        history.data[message.from_user.id]["photo_check"] = 0
        photo_check_and_post(message)
    else:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_num(message):

    # Store the number of photos that need to be posted in history.data. Forwards to results.
    try:
        history.data[message.from_user.id]["photo_count"] = int(message.text)
        if history.data[message.from_user.id]["photo_count"] < 1 or history.data[message.from_user.id][
            "photo_count"] > 3:
            bot.send_message(message.from_user.id, "Wrong input. 1-3 photos only")
        else:
            photo_check_and_post(message)
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_check_and_post(message):

    # Uses the information from history.data to form and send a request to hotel api through hotel_data function.
    # Logs the query results into history.log for future use in /history command. Posts the results to user.
    try:
        bot.send_message(message.from_user.id, "Wait for results")
        hotel_data = hotel_request(message)
        hotel_list = hotel_compute(hotel_data)
        hotels = list(hotel_list.keys())
        log(message, command=history.data[message.from_user.id]["command"],
            city=history.data[message.from_user.id]["city"], hotels=hotels)
        for key, value in hotel_list.items():
            bot.send_message(message.from_user.id, key)
            if history.data[message.from_user.id]["photo_check"] == 1:
                for i in range(history.data[message.from_user.id]["photo_count"]):
                    bot.send_photo(message.from_user.id, photo=value[i])
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def lowprice(message):

    # Changes sorting method for lowest price possible
    history.data[message.from_user.id] = {"command": "lowprice", "sort": "PRICE_LOW_TO_HIGH", "maxprice": 10000, "minprice": 10}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    bot.register_next_step_handler(message, fetch_city)


def highprice(message):

    # Changes sorting method for highest price possible
    history.data[message.from_user.id] = {"command": "highprice", "sort": "PRICE_HIGH_TO_LOW", "maxprice": 10000, "minprice": 10}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    bot.register_next_step_handler(message, fetch_city)


def bestdeal(message):

    # Changes sorting method to distance from the city center. Missing price arguments compared to other commands
    # since those are added by user further down the line.
    history.data[message.from_user.id] = {"command": "bestdeal", "sort": "DISTANCE"}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    history.price_sort = "DISTANCE"
    bot.register_next_step_handler(message, fetch_city)


def histor(message):

    # Weird function name due to conflict with the history object from History class that is used to store data.
    # Didn't think this through. Pulls the history of user queries based on their telegram id from history.log.
    bot.send_message(message.from_user.id, "History of your requests:")
    try:
        if message.from_user.id in history.log:
            for key, value in history.log[message.from_user.id].items():
                bot.send_message(message.from_user.id, f"{key} - {value[0]} in {value[1]}. Hotels found: {', '.join(value[2])}")
        else:
            bot.send_message(message.from_user.id, "Your history is empty")
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")

def helper(message):

    # Quick info on available commands
    bot.send_message(message.from_user.id, "Please use\n/lowprice for hotels with the lowest price in a given "
                                           "city\n/highprice for hotels with the highest price\n/bestdeal for the "
                                           "hotels closest to the city centre\n/history to see the history of your "
                                           "requests")

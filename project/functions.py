import datetime
import os

import requests
from dotenv import load_dotenv

from history import history

load_dotenv()
hotel_API_KEY = os.getenv("hotels_API_KEY")


def log(message, command, city, hotels):
    if message.from_user.id not in history.log:
        history.log[message.from_user.id] = dict()
    history.log[message.from_user.id][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = [command, city, hotels]


def hotel_request(message):
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
            "max": 100000,
            "min": 10
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
    hotels = dict()

    for cur_hotel in data:
        hotels[cur_hotel.get('name')] = get_pictures(cur_hotel.get("id"))
        # hotel['price'] = hotel_price(cur_hotel)

    return hotels


def get_pictures(hotel_id):
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

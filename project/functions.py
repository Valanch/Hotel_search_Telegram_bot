import os

import requests
from dotenv import load_dotenv

from history import history

load_dotenv()
hotel_API_KEY = os.getenv("hotels_API_KEY")


# def fetch_city(message):  # gets the city from message, puts it in history dict, goes to get number of hotels
#     try:
#         city = message.text.strip()
#         history.log[history.num] = city
#         bot.send_message(message.from_user.id, "How many hotels?")
#         bot.register_next_step_handler(message, fetch_hotel_num)
#     except Exception:
#         bot.send_message(message.from_user.id, "Something went wrong, start over.")
#
#
# def fetch_hotel_num(message):  # gets the number of hotels, ties it to the requested city, forwards to results
#     try:
#         hotel_num = int(message.text)
#         history.hotel_num = hotel_num
#         bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
#         bot.register_next_step_handler(message, photo_check_and_post)
#     except Exception:
#         bot.send_message(message.from_user.id, "Something went wrong, start over.")
#
#
# def photo_check_and_post(message):  # checks if the picture needs to be fetched. Gets the data for
#     # requested city for requested number of hotels, sorted low to high price. Sends
#     # results to user.
#     try:
#         if message.text.lower() == "yes":
#             photos = 1
#         elif message.text.lower() == "no":
#             photos = 0
#         else:
#             bot.send_message(message.from_user.id, f"Something went wrong. {message.text.lower()} Start over.")
#
#         url = "https://hotels4.p.rapidapi.com/locations/v3/search"
#         querystring = {"q": history.log[history.num]}
#         headers = {
#             "X-RapidAPI-Key": hotel_API_KEY,
#             "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#         }
#         response = requests.request("GET", url, headers=headers, params=querystring)
#         data = response.json()
#         location_id = data["sr"][0]['gaiaId']
#         bot.send_message(message.from_user.id, "Wait for results")
#         url = "https://hotels4.p.rapidapi.com/properties/v2/list"
#
#         payload = {
#             "currency": "USD",
#             "eapid": 1,
#             "locale": "en_US",
#             "siteId": 300000001,
#             "destination": {"regionId": location_id},
#             "checkInDate": {
#                 "day": 10,
#                 "month": 10,
#                 "year": 2022
#             },
#             "checkOutDate": {
#                 "day": 15,
#                 "month": 10,
#                 "year": 2022
#             },
#             "rooms": [
#                 {
#                     "adults": 2,
#                     "children": [{"age": 5}, {"age": 7}]
#                 }
#             ],
#             "resultsStartingIndex": 0,
#             "resultsSize": history.hotel_num,
#             "sort": "PRICE_LOW_TO_HIGH",
#             "filters": {"price": {
#                 "max": 150,
#                 "min": 10
#             }}
#         }
#         headers = {
#             "content-type": "application/json",
#             "X-RapidAPI-Key": hotel_API_KEY,
#             "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#         }
#
#         response = requests.request("POST", url, json=payload, headers=headers)
#         hotel_data = response.json()
#         hotel_data = hotel_data.get("data").get("propertySearch").get("properties")
#         # print(hotel_data)
#         hotel_list = hotel_compute(hotel_data)
#         # print(hotel_list)
#         for key, value in hotel_list.items():
#             bot.send_message(message.from_user.id, key)
#             if photos == 1:
#                 bot.send_photo(message.from_user.id, photo=value)
#     except Exception:
#         bot.send_message(message.from_user.id, "Something went wrong, start over.")

def hotel_request():
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": history.log[history.num]}
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
            "month": 10,
            "year": 2022
        },
        "checkOutDate": {
            "day": 15,
            "month": 10,
            "year": 2022
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": history.hotel_num,
        "sort": history.price_sort,
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

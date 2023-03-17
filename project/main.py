import json
import os
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)
hotel_API_KEY = os.getenv("hotels_API_KEY")


class History:  # work in progress, will track individual users' logs

    def __init__(self, log_dict, num=0, hotel_num=0, hotels=None):
        self.log = log_dict
        self.num = num
        self.hotel_num = hotel_num
        self.hotels = hotels


history = History(log_dict=dict())


def fetch_city(message):  # gets the city from message, puts it in history dict, goes to get number of hotels
    city = message.text.strip()
    history.log[history.num] = city
    bot.send_message(message.from_user.id, f"You chose {city}")
    bot.send_message(message.from_user.id, "How many hotels?")
    bot.register_next_step_handler(message, fetch_hotel_num)


def fetch_hotel_num(message):  # gets the number of hotels, ties it to the requested city, forwards to results
    hotel_num = int(message.text)
    history.hotel_num = hotel_num
    bot.send_message(message.from_user.id, f"You want {hotel_num} hotels")
    bot.send_message(message.from_user.id, f"Your city is {history.log[history.num]}")
    bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
    bot.register_next_step_handler(message, photo_check_and_post)


def photo_check_and_post(message):  # checks if the picture needs to be fetched. Gets the data for
    # requested city for requested number of hotels, sorted low to high price. Sends
    # results to user.
    if message.text.lower() == "yes":
        photos = 1
        bot.send_message(message.from_user.id, "getting photos")
    elif message.text.lower() == "no":
        photos = 0
        bot.send_message(message.from_user.id, "not getting photos")
    else:
        bot.send_message(message.from_user.id, f"Something went wrong. {message.text.lower()} Start over.")

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": history.log[history.num]}
    headers = {
        "X-RapidAPI-Key": hotel_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    location_id = data["sr"][0]['gaiaId']
    bot.send_message(message.from_user.id, "ok")
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
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 150,
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
    # print(hotel_data)
    hotel_list = hotel_compute(hotel_data)
    # print(hotel_list)
    for key, value in hotel_list.items():
        bot.send_message(message.from_user.id, key)
        if photos == 1:
            bot.send_photo(message.from_user.id, photo=value)


def hotel_compute(data):
    hotels = dict()

    for cur_hotel in data:
        hotels[cur_hotel.get('name')] = cur_hotel.get("propertyImage").get("image").get("url")
        # hotel['price'] = hotel_price(cur_hotel)

    return hotels


def lowprice(message):
    history.num += 1
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    bot.register_next_step_handler(message, fetch_city)


@bot.message_handler(commands=["hello-world", "lowprice"])
def send_welcome(message):
    if message.text == "/hello-world":
        bot.reply_to(message, "Hello world")
    if message.text == "/lowprice":
        lowprice(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Thank you for switching to English")
    else:
        bot.send_message(message.from_user.id, "Try saying something else")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

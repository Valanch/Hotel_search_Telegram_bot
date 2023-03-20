import json
import os
import requests
import telebot

from dotenv import load_dotenv
from history import history
from functions import hotel_request, hotel_compute


load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)
hotel_API_KEY = os.getenv("hotels_API_KEY")

# class History:  # work in progress, will track individual users' logs
#
#     def __init__(self, log_dict, num=0, hotel_num=0, hotels=None):
#         self.log = log_dict
#         self.num = num
#         self.hotel_num = hotel_num
#         self.hotels = hotels
#
#
#history = History(log_dict=dict())


def fetch_city(message):  # gets the city from message, puts it in history dict, goes to get number of hotels
    try:
        city = message.text.strip()
        history.log[history.num] = city
        bot.send_message(message.from_user.id, "How many hotels?")
        bot.register_next_step_handler(message, fetch_hotel_num)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def fetch_hotel_num(message):  # gets the number of hotels, ties it to the requested city, forwards to results
    try:
        hotel_num = int(message.text)
        history.hotel_num = hotel_num
        bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
        bot.register_next_step_handler(message, photo_check)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_check(message):
    if message.text.lower() == "yes":
        history.photo_check = 1
        bot.send_message(message.from_user.id, "How many pictures per hotel? 1-3")
        bot.register_next_step_handler(message, photo_num)
    elif message.text.lower() == "no":
        history.photo_check = 0
        photo_check_and_post(message)
    else:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_num(message):
    try:
        history.photo_count = int(message.text)
        if history.photo_count < 1 or history.photo_count > 3:
            bot.send_message(message.from_user.id, "Wrong input. 1-3 photos only")
        else:
            photo_check_and_post(message)
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_check_and_post(message):  # checks if the picture needs to be fetched. Gets the data for
    # requested city for requested number of hotels, sorted low to high price. Sends
    # results to user.
    try:
        bot.send_message(message.from_user.id, "Wait for results")
        hotel_data = hotel_request()
        print(hotel_data)
        hotel_list = hotel_compute(hotel_data)
        print(hotel_list)
        for key, value in hotel_list.items():
            bot.send_message(message.from_user.id, key)
            if history.photo_check == 1:
                for i in range(history.photo_count):
                    bot.send_photo(message.from_user.id, photo=value[i])
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


# def hotel_compute(data):
#     hotels = dict()
#
#     for cur_hotel in data:
#         hotels[cur_hotel.get('name')] = cur_hotel.get("propertyImage").get("image").get("url")
#         # hotel['price'] = hotel_price(cur_hotel)
#
#     return hotels
#
# def get_pictures(hotel_id):
#     url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
#
#     payload = {
#         "currency": "USD",
#         "eapid": 1,
#         "locale": "en_US",
#         "siteId": 300000001,
#         "propertyId": hotel_id
#     }
#     headers = {
#         "content-type": "application/json",
#         "X-RapidAPI-Key": "046ce92f3fmsh1f3fee9b942b3d9p123f1bjsn8e796bb748da",
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#     }
#
#     response = requests.request("POST", url, json=payload, headers=headers)

def lowprice(message):
    history.num += 1
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    history.price_sort = "PRICE_LOW_TO_HIGH"
    bot.register_next_step_handler(message, fetch_city)
    # bot.send_message(message.from_user.id, "How many hotels?")
    # bot.register_next_step_handler(message, fetch_hotel_num)
    # bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
    # bot.register_next_step_handler(message, photo_check_and_post)
    # hotel_list, photos = photo_check_and_post(message)
    # for key, value in hotel_list.items():
    #     bot.send_message(message.from_user.id, key)
    #     if photos == 1:
    #         bot.send_photo(message.from_user.id, photo=value)


def highrice(message):
    history.num += 1
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    history.price_sort = "PRICE_HIGH_TO_LOW"
    bot.register_next_step_handler(message, fetch_city)


@bot.message_handler(commands=["hello-world", "lowprice", "highprice"])
def send_welcome(message):
    if message.text == "/hello-world":
        bot.reply_to(message, "Hello world")
    if message.text == "/lowprice":
        lowprice(message)
    if message.text == "/highprice":
        highrice(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Thank you for switching to English")
    else:
        bot.send_message(message.from_user.id, "Try saying something else")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

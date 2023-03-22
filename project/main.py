import datetime
import json
import os
import requests
import telebot

from dotenv import load_dotenv
from history import history
from functions import hotel_request, hotel_compute, log

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)
hotel_API_KEY = os.getenv("hotels_API_KEY")


def fetch_city(message):  # gets the city from message, puts it in history dict, goes to get number of hotels
    try:
        city = message.text.strip()
        history.data[message.from_user.id]["city"] = city
        print(history.data)
        bot.send_message(message.from_user.id, "How many hotels?")
        bot.register_next_step_handler(message, fetch_hotel_num)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def fetch_hotel_num(message):  # gets the number of hotels, ties it to the requested city, forwards to results
    try:
        hotel_num = int(message.text)
        history.data[message.from_user.id]["number"] = hotel_num
        bot.send_message(message.from_user.id, "Do you want pictures? Yes / No")
        bot.register_next_step_handler(message, photo_check)
    except Exception:
        bot.send_message(message.from_user.id, "Something went wrong, start over.")


def photo_check(message):
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


def photo_check_and_post(message):  # checks if the picture needs to be fetched. Gets the data for
    # requested city for requested number of hotels, sorted low to high price. Sends
    # results to user.
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
    history.data[message.from_user.id] = {"command": "lowprice", "sort": "PRICE_LOW_TO_HIGH"}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    bot.register_next_step_handler(message, fetch_city)


def highrice(message):
    history.data[message.from_user.id] = {"command": "highprice", "sort": "PRICE_HIGH_TO_LOW"}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    bot.register_next_step_handler(message, fetch_city)


def bestdeal(message):
    history.data[message.from_user.id] = {"command": "bestdeal", "sort": "DISTANCE"}
    bot.send_message(message.from_user.id, "Which city are we searching in?")
    history.price_sort = "DISTANCE"
    bot.register_next_step_handler(message, fetch_city)


def histor(message):
    print(history.log)
    bot.send_message(message.from_user.id, "History of your requests:")
    for key, value in history.log[message.from_user.id].items():
        bot.send_message(message.from_user.id, f"{key} - {value[0]} in {value[1]}. Hotels found: {', '.join(value[2])}")


@bot.message_handler(commands=["hello-world", "lowprice", "highprice", "bestdeal", "history"])
def send_welcome(message):
    if message.text == "/hello-world":
        bot.reply_to(message, "Hello world")
    if message.text == "/lowprice":
        lowprice(message)
    if message.text == "/highprice":
        highrice(message)
    if message.text == "/bestdeal":
        bestdeal(message)
    if message.text == "/history":
        histor(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Thank you for switching to English")
    else:
        bot.send_message(message.from_user.id, "Try saying something else")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

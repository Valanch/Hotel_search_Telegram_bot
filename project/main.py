from functions import lowprice, highprice, bestdeal, histor, helper
from loader import bot



@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Welcome to the hotel bot")
    if message.text == "/help":
        helper(message)


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history"])
def execute_command(message):
    if message.text == "/lowprice":
        lowprice(message)
    if message.text == "/highprice":
        highprice(message)
    if message.text == "/bestdeal":
        bestdeal(message)
    if message.text == "/history":
        histor(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Thank you for switching to English")
    else:
        bot.send_message(message.from_user.id, "Please refer to the /help command")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

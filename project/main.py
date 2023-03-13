import telebot

bot = telebot.TeleBot("6205848362:AAGWdx5uJ-TahvfqO3PEuUiyHkM44R9LhYM")


@bot.message_handler(commands=['hello-world'])
def send_welcome(message):
    bot.reply_to(message, "Hello world")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Thank you for switching to English")
    else:
        bot.send_message(message.from_user.id, "Try saying something else")


bot.polling(none_stop=True, interval=0)

import telebot
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN_TELEGRAM_BOT')

bot = telebot.TeleBot(API_TOKEN)

welcome_message = 'Добро пожаловать!!'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Я готов к работе!')

@bot.message_handler(commands=['set_wlc_msg'])
def set_welcome_message(message):
    if message.chat.type != 'private':
        admins = [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)]
        if message.from_user.id in admins:
            global welcome_message
            welcome_message = " ".join(message.text.split()[1:])
            bot.reply_to(message, f'Приветственное сообщение установлено: {welcome_message}')
        else:
            bot.reply_to(message, 'Вы должны быть администратором, чтобы изменить приветственное сообщение.')

@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(content_types=['voice', 'video'])
def delete_voice_video_messages(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.reply_to(message, 'Надеюсь, ты не сильно старался..')

if __name__ == '__main__':
    bot.polling(none_stop=True)
    
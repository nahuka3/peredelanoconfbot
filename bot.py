import telebot
from telebot import types
from dotenv import load_dotenv
import os
import logging

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN_TELEGRAM_BOT')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(API_TOKEN)

welcome_messages = {}

def send_message(chat_id, message_text):
    logger.info(f"Sent message to chat {chat_id}: {message_text}")
    bot.send_message(chat_id, message_text)

@bot.message_handler(commands=['start'])
def start(message):
    send_message(message.chat.id, 'Я готов к работе!')

@bot.message_handler(commands=['set_wlc_msg'])
def set_welcome_message(message):
    if message.chat.type != 'private':
        admins = [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)]
        if message.from_user.id in admins:
            welcome_text = ' '.join(message.text.split(' ')[1:]) # Get the text after the command
            welcome_messages[message.chat.id] = welcome_text
            send_message(message.chat.id, f'Приветственное сообщение установлено: {welcome_messages[message.chat.id]}')
            bot.delete_message(message.chat.id, message.message_id) # Delete the set_wlc_msg command message
        else:
            send_message(message.chat.id, 'Вы должны быть администратором, чтобы изменить приветственное сообщение.')

@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    bot.delete_message(message.chat.id, message.message_id)
    new_member = message.new_chat_members[0]
    username = new_member.username if new_member.username else new_member.first_name
    if message.chat.id in welcome_messages:
        send_message(message.chat.id, f"{welcome_messages[message.chat.id]} @{username}")
    else:
        send_message(message.chat.id, f"Добро пожаловать, @{username}!")

@bot.message_handler(content_types=['voice', 'video'])
def delete_voice_video_messages(message):
    bot.delete_message(message.chat.id, message.message_id)
    send_message(message.chat.id, 'Надеюсь, ты не сильно старался..')

if __name__ == '__main__':
    logger.info('Бот запущен')
    bot.polling(none_stop=True)

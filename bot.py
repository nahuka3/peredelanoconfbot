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
last_welcome_messages = {}
is_bot_active = {}

def send_message(chat_id, message_text):
    logger.info(f"Sent message to chat {chat_id}: {message_text}")
    message = bot.send_message(chat_id, message_text)
    return message.message_id

def is_user_admin(chat_id, user_id):
    admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    return user_id in admins

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != 'private' and not is_user_admin(message.chat.id, message.from_user.id):
        send_message(message.chat.id, 'Только администратор может выполнить эту команду.')
        return
    is_bot_active[message.chat.id] = True
    send_message(message.chat.id, 'Я готов к работе!')

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.chat.type != 'private' and not is_user_admin(message.chat.id, message.from_user.id):
        send_message(message.chat.id, 'Только администратор может выполнить эту команду.')
        return
    is_bot_active[message.chat.id] = False
    send_message(message.chat.id, 'Бот остановлен.')

@bot.message_handler(commands=['set_wlc_msg'])
def set_welcome_message(message):
    if message.chat.type != 'private' and not is_user_admin(message.chat.id, message.from_user.id):
        send_message(message.chat.id, 'Только администратор может выполнить эту команду.')
        return

    if not is_bot_active.get(message.chat.id, True):
        return

    welcome_text = ' '.join(message.text.split(' ')[1:]) # Get the text after the command
    welcome_messages[message.chat.id] = welcome_text
    send_message(message.chat.id, f'Приветственное сообщение установлено: {welcome_messages[message.chat.id]}')
    bot.delete_message(message.chat.id, message.message_id) # Delete the set_wlc_msg command message

@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    if not is_bot_active.get(message.chat.id, True):
        return

    bot.delete_message(message.chat.id, message.message_id)
    new_member = message.new_chat_members[0]
    username = new_member.username if new_member.username else new_member.first_name

    # Delete last welcome message if exists
    if message.chat.id in last_welcome_messages:
        try:
            bot.delete_message(message.chat.id, last_welcome_messages[message.chat.id])
        except Exception as e:
            logger.warning(f"Unable to delete last welcome message: {e}")

    # Send new welcome message
    if message.chat.id in welcome_messages:
        new_welcome_message_id = send_message(message.chat.id, f"{welcome_messages[message.chat.id]} @{username}")
    else:
        new_welcome_message_id = send_message(message.chat.id, f"Добро пожаловать, @{username}!")

    # Save new welcome message ID
    last_welcome_messages[message.chat.id] = new_welcome_message_id

@bot.message_handler(content_types=['voice', 'video'])
def delete_voice_video_messages(message):
    if not is_bot_active.get(message.chat.id, True):
        return

    bot.delete_message(message.chat.id, message.message_id)
    send_message(message.chat.id, 'Надеюсь, ты не сильно старался..')

if __name__ == '__main__':
    logger.info('Бот запущен')
    bot.polling(none_stop=True)

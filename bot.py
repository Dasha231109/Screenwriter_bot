# your_GPTassistant_bot
# -----------------------------------------------------ИМПОРТЫ----------------------------------------------------------
import logging
import telebot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, Message
from config import *
# from gpt import GPT
# from database import *

# gpt = GPT()

bot = TeleBot(TOKEN)
MAX_LETTERS = MAX_TOKENS

# ------------------------------------------------------ЛОГГИРОВАНИЕ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


@bot.message_handler(commands=['debug'])
def send_logs(message):
    user_id = message.chat.id
    if user_id == 1377946178:
        try:
            with open("log_file.txt", "rb") as f:
                bot.send_document(message.chat.id, f)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, "Простите, но я не могу предоставить вам логи, так как их нет.")
    else:
        bot.send_message(message.chat.id, "Вы не можете пользоваться этой командой, так как у вас недостаточно прав.")
# --------------------------------------------------------СПИСКИ--------------------------------------------------------
genres = ['Комедия', 'Детектив', 'Мистика']

# ---------------------------------------------------------БОТ----------------------------------------------------------
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    if message.text == '/start':
        name_user = message.from_user.first_name
        logging.info("Отправка приветственного сообщения")
        bot.send_message(message.chat.id, text=f"Привет, {name_user}\n"
                                               f"Я бот-сценарист, который может помочь с созданием уникальных и "
                                               f"интересных историй. Напиши /new_story чтобы создать новую историю. "
                                               f"Чтобы закончить пиши /end.",
                         reply_markup=create_keyboard(['/new_story']))
    if message.text == '/help':
        logging.info("Отправка помощи")
        bot.send_message(message.chat.id, text='Запустите бот командой /start\n'
                                               'Начните новую историю командой /new_story\n'
                                               'Выберите жанр/главного героя/сеттинг\b'
                                               'Подождите пока история сгенерируется\n'
                                               'Напишите сообщение связанное с историей чтобы изменить продолжение '
                                               'истории и я продолжу вашу историю учитывая ваше сообщение или завершите '
                                               'историю введя команду /end',
                         reply_markup=create_keyboard(['/new_story']))


@bot.message_handler(commands=['new_story'])
def story(message):
    bot.send_message(message.chat.id, text='Хорошо, давайте начнем! Какой жанр истории вы бы хотели?',
                     reply_markup=create_keyboard(genres))
    bot.register_next_step_handler()


def genre(message):


bot.infinity_polling()

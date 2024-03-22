# your_GPTassistant_bot
# -----------------------------------------------------ИМПОРТЫ----------------------------------------------------------
import logging
import telebot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
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


# ----------------------------------------------------СПИСКИ И СЛОВАРИ--------------------------------------------------
genres = ['Комедия', 'Детектив', 'Мистика']
main_characters = ['Буратино', 'Крош', 'Шерлок Хомс', 'Мисс Марпл', 'Аннабель', 'Волан де Морт']
locations = ['Пятерочка', 'Домик в деревне', 'Заколдованный замок']

current_genres = {}
current_characters = {}
current_locations = {}
information = {}


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
                                               'истории и я продолжу вашу историю учитывая ваше сообщение или '
                                               'завершите историю введя команду /end',
                         reply_markup=create_keyboard(['/new_story']))


@bot.message_handler(commands=['new_story'])
def story(message):
    bot.send_message(message.chat.id, text='Хорошо, давайте начнем! Какой жанр истории вы бы хотели?',
                     reply_markup=create_keyboard(genres))
    bot.register_next_step_handler(message, choose_genre)


def choose_genre(message):
    user_id = message.from_user.id
    genre = message.text

    if genre in genres:
        current_genres[user_id] = genre
        print(current_genres)
        bot.send_message(message.chat.id, text='Хорошо, выбери главного героя',
                         reply_markup=create_keyboard(main_characters))
        bot.register_next_step_handler(message, choose_characters)
    else:
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)


def choose_characters(message):
    user_id = message.from_user.id
    character = message.text

    if character in main_characters:
        current_characters[user_id] = character
        print(current_characters)
        bot.send_message(message.chat.id, text='Отличный выбор, выбери сеттинг:\n'
                                               '1) Пятерочка - cтрашный магазин, полон ужасов, находится один в '
                                               'дремучем лесу.\n'
                                               '2) Домик в деревне - маленький уютный домик, рядом растут деревья и '
                                               'протекает река.\n'
                                               '3) Заколдованный Замок - древнее место, окутанное тайнами и '
                                               'легендами, находится в центре города.',
                         reply_markup=create_keyboard(locations))
        bot.register_next_step_handler(message, choose_locations)
    else:
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(main_characters))
        bot.register_next_step_handler(message, choose_characters)


def choose_locations(message):
    user_id = message.from_user.id
    location = message.text

    if location in locations:
        current_locations[user_id] = location
        print(current_locations)
        bot.send_message(message.chat.id, "Супер! Получится крутая история, а чтобы она получилась еще круче можешь "
                                          "написать дополнительную информацию. Если хочешь уже начать пиши /begin")
        bot.register_next_step_handler(message, add_info)
    else:
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(locations))
        bot.register_next_step_handler(message, choose_locations)


def add_info(message):
    user_id = message.from_user.id
    info = str(message.text)
    if info != "/begin":
        information[user_id] = info
        print(information)
        bot.send_message(message.chat.id, 'Отлично, вся информация будет учтена в истории. Чтобы начать введите /begin')
    else:
        information[user_id] = None
        print(information)


bot.infinity_polling()

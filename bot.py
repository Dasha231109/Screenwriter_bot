# your_GPTassistant_bot
# -----------------------------------------------------ИМПОРТЫ----------------------------------------------------------
import sqlite3
import types

import telebot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
import datetime
from gpt import *
from database import *

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

current_choose = {}


# ---------------------------------------------------------БОТ----------------------------------------------------------
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    time = datetime.datetime.now()
    user_id = message.from_user.id

    if message.text == '/start':
        create_db()
        logging.info('Создали бд')

        create_table(DB_TABLE_USERS_NAME)
        logging.info('Создали таблицу если ее нет')

        values = [user_id, 'None', 'None', time, 0, 0]
        insert_row(values)
        logging.info('Записали значения')

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
    if is_limit_users():
        bot.send_message(message.chat.id, "Извините, но количество пользователей превышено. Бот недоступен.")
        exit()

    logging.info('Новая история')
    user_id = message.from_user.id
    time = datetime.datetime.now()

    session_id = get_data_for_user(user_id, "session_id")[0][0]
    session_id += 1
    values = [user_id, 'None', 'None', time, 1, session_id]
    insert_row(values)
    logging.info('Записали значение сессии')

    if is_limit_sessions_id(user_id):
        if session_id == MAX_SESSIONS - 1:
            bot.send_message(message.chat.id, "Осталась 1 доступная сессия")
            logging.info("Сообщили о том, что сессии заканчиваются")
        else:
            logging.info("Сообщили о том, что сессии закончились")
            bot.send_message(message.chat.id, "Извините, но у вас закончились доступные сессии. Бот недоступен")
            exit()

    bot.send_message(message.chat.id, text='Хорошо, давайте начнем! Какой жанр истории вы бы хотели?',
                     reply_markup=create_keyboard(genres))
    bot.register_next_step_handler(message, choose_genre)


def choose_genre(message):
    user_id = message.from_user.id
    genre = message.text

    if genre not in genres:
        logging.info('Пользователь ввел не жанр')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)
        return

    current_choose[user_id] = {}
    current_choose[user_id]['genre'] = genre
    logging.info('Сохранили жанр в словарь')
    print(current_choose)

    bot.send_message(message.chat.id, text='Хорошо, выберите главного героя',
                     reply_markup=create_keyboard(main_characters))
    bot.register_next_step_handler(message, choose_characters)


def choose_characters(message):
    user_id = message.from_user.id
    character = message.text

    if character not in main_characters:
        logging.info('Пользователь ввел не персонажа')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(main_characters))
        bot.register_next_step_handler(message, choose_characters)

    current_choose[user_id]['character'] = character
    logging.info('Сохранили персонажа в словарь')
    print(current_choose)

    bot.send_message(message.chat.id, text='Отличный выбор, выберите сеттинг:\n'
                                           '1) Пятерочка - cтрашный магазин, полон ужасов, находится один в '
                                           'дремучем лесу.\n'
                                           '2) Домик в деревне - маленький уютный домик, рядом растут деревья и '
                                           'протекает река.\n'
                                           '3) Заколдованный Замок - древнее место, окутанное тайнами и '
                                           'легендами, находится в центре города.',
                     reply_markup=create_keyboard(locations))
    bot.register_next_step_handler(message, choose_locations)


def choose_locations(message):
    user_id = message.from_user.id
    location = message.text

    if location not in locations:
        logging.info('Пользователь ввел не сеттинг')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(locations))
        bot.register_next_step_handler(message, choose_locations)

    current_choose[user_id]['location'] = location
    logging.info('Сохранили сеттинг в словарь')
    print(current_choose)

    bot.send_message(message.chat.id, text="Супер! Получится крутая история, а чтобы она получилась еще круче можешь "
                                           "написать дополнительную информацию. Если хочешь уже начать пиши /begin",
                     reply_markup=create_keyboard(['/begin']))
    bot.register_next_step_handler(message, add_info)


def add_info(message):
    user_id = message.from_user.id
    info = message.text

    if info != '/begin':
        current_choose[user_id]['info'] = info
        logging.info('Сохранили доп. инфо. в словарь')
        print(current_choose)
        bot.send_message(message.chat.id, text='Отлично, вся информация будет учтена в истории. Чтобы начать введите '
                                               '/begin',
                         reply_markup=create_keyboard(['/begin']))
    else:
        begin_story(message)


@bot.message_handler(commands=['begin'])
def begin_story(message):
    user_id = message.from_user.id

    if get_data_for_user(user_id, 'session_id')[0][0] == 0:
        bot.send_message(message.chat.id, text="Чтобы начать новую историю введите команду /new_story, и ответьте "
                                               "пройдите опрос.",
                         reply_markup=create_keyboard(['/new_story']))

    if not current_choose[user_id]['genre']:
        bot.send_message(message.chat.id, text="Кажется, вы не выбрали жанр, пожалуйста выберите один из предложенных "
                                               "вариантов.",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)

    if not current_choose[user_id]['character']:
        bot.send_message(message.chat.id, text="Кажется, вы не выбрали героя, пожалуйста выберите один из предложенных "
                                               "вариантов.",
                         reply_markup=create_keyboard(main_characters))
        bot.register_next_step_handler(message, choose_characters)

    if not current_choose[user_id]['location']:
        bot.send_message(message.chat.id, text="Кажется, вы не выбрали сеттинг, пожалуйста выберите один из "
                                               "предложенных вариантов.",
                         reply_markup=create_keyboard(locations))
        bot.register_next_step_handler(message, choose_locations)

    start_story()


@bot.message_handler(content_types=['text'])
def start_story(message: types.Message, mode='continue'):
    user_id: int = message.from_user.id
    user_message: str = message.text

    if mode == 'end':
        user_message = END_STORY

    row: sqlite3.Row = get_data_for_user(user_id, 'session_id')
    collection: sqlite3.Row = get_dialogue_for_user(user_id, row['session_id'])
    collection.append({'role': 'user', 'content': user_message})

    tokens: int = count_tokens_in_dialogue(collection)
    if is_limit_tokens(user_id, tokens):
        return False

    update_row_value(user_id, 'role', 'user', 'user_id', user_id)
    update_row_value(user_id, 'content', user_message, 'role', 'user')


@bot.message_handler(commands=['all_tokens'])
def send_tokens(message):
    try:
        all_tokens = 'count_all_tokens_from_db()'
        bot.send_message(message.chat.id, text=f'За все время использования бота\n'
                                               f'Израсходовано токенов - {all_tokens}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Извините. произошла ошибка: {e}')


start_story()

bot.infinity_polling()

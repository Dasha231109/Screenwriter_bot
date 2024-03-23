# your_GPTassistant_bot
# -----------------------------------------------------ИМПОРТЫ----------------------------------------------------------
import telebot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from telebot import types
import datetime
from gpt import *
from database import *

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

user_data = {}


# ---------------------------------------------------------БОТ----------------------------------------------------------
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start', 'help'])
def commands(message):
    user_id = message.from_user.id

    if message.text == '/start':
        user_data[user_id] = {
            'session_id': 0,
            'genre': None,
            'character': None,
            'location': None,
            'info': None,
            'test_mode': False,
            'new_story': None
        }

        create_db()
        logging.info('Создали бд')

        create_table(DB_TABLE_USERS_NAME)
        logging.info('Создали таблицу если ее нет')

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
    user_id = message.from_user.id

    if is_limit_users():
        bot.send_message(message.chat.id, "Извините, но количество пользователей превышено. Бот недоступен.")
        return

    try:
        user_data[user_id]['new_story'] = "в истории"
        logging.info('Новая история')

        bot.send_message(message.chat.id, text='Хорошо, давайте начнем! Какой жанр истории вы бы хотели?',
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)

    except KeyError:
        bot.send_message(message.chat.id, text="Чтобы начать введите команду /start",
                         reply_markup=create_keyboard(['/start']))


def choose_genre(message):
    user_id = message.from_user.id
    genre = message.text

    if genre not in genres:
        logging.info('Пользователь ввел не жанр')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)
        return

    user_data[user_id]['genre'] = genre
    logging.info('Сохранили жанр в словарь')

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
        return

    user_data[user_id]['character'] = character
    logging.info('Сохранили персонажа в словарь')

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
        return

    user_data[user_id]['location'] = location
    logging.info('Сохранили сеттинг в словарь')

    bot.send_message(message.chat.id, text="Супер! Получится крутая история, а чтобы она получилась еще круче можешь "
                                           "написать дополнительную информацию. Если хочешь уже начать пиши /begin",
                     reply_markup=create_keyboard(['/begin']))
    bot.register_next_step_handler(message, add_info)


def add_info(message):
    user_id = message.from_user.id
    info = message.text

    if info != '/begin':
        user_data[user_id]['info'] = info
        logging.info('Сохранили доп. инфо. в словарь')
        bot.send_message(message.chat.id, text='Отлично, вся информация будет учтена в истории. Чтобы начать введите '
                                               '/begin',
                         reply_markup=create_keyboard(['/begin']))
    else:
        begin_story(message)


@bot.message_handler(commands=['begin'])
def begin_story(message):
    user_id = message.from_user.id

    try:
        if not user_data[user_id]['new_story']:
            bot.send_message(message.chat.id, text="Чтобы начать новую историю введите команду /new_story, и "
                                                   "пройдите опрос.",
                             reply_markup=create_keyboard(['/new_story']))
        elif not user_data[user_id]['genre']:
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали жанр, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(genres))
            bot.register_next_step_handler(message, choose_genre)

        elif not user_data[user_id]['character']:
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали героя, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(main_characters))
            bot.register_next_step_handler(message, choose_characters)

        elif not user_data[user_id]['location']:
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали сеттинг, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(locations))
            bot.register_next_step_handler(message, choose_locations)

    except KeyError:
        bot.send_message(message.chat.id, text="Чтобы начать введите команду /start",
                         reply_markup=create_keyboard(['/start']))

    get_story(message)


@bot.message_handler(content_types=['text'])
def start_story(message: types.Message, mode='continue'):
    user_id = message.from_user.id
    user_message = message.text
    time = datetime.datetime.now()

    if mode == 'end':
        user_message = END_STORY

    session_id: int = get_data_for_user(user_id, 'session_id')[0][0]
    collection = get_dialogue_for_user(user_id, session_id)
    collection.append({'role': 'user', 'text': user_message})

    tokens = count_tokens_in_dialogue(collection)
    print(tokens)
    if is_limit_tokens(user_id, tokens):
        return

    values = [user_id, 'user', user_message, time, tokens, session_id]
    insert_row(values)

    if is_limit_tokens(user_id, tokens):
        return

    gpt_text, result_for_test = ask_gpt(collection, mode)  # изменить ask_gpt

    collection = get_dialogue_for_user(user_id, session_id)
    collection.append({'role': 'assistant', 'text': gpt_text})
    tokens: int = count_tokens_in_dialogue(collection)

    values = [user_id, 'assistant', gpt_text, time, tokens, session_id]
    insert_row(values)

    if not user_data[user_id]['test_mode']:
        bot.send_message(message.chat.id, text=gpt_text,
                         reply_markup=create_keyboard(['/end']))
    else:
        bot.send_message(message.chat.id, text=result_for_test,
                         reply_markup=create_keyboard(['/end']))


@bot.message_handler(content_types=['text'])
def get_story(message: types.Message):
    user_id = message.from_user.id
    time = datetime.datetime.now()

    session_id = 1
    if is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        row = get_data_for_user(user_id, 'session_id')[0][0]
        session_id = row + 1
        print(session_id)

    if is_limit_sessions_id(user_id):
        if session_id == MAX_SESSIONS:
            bot.send_message(message.chat.id, "Осталась 1 доступная сессия")
            logging.info("Сообщили о том, что сессии заканчиваются")
        else:
            logging.info("Сообщили о том, что сессии закончились")
            bot.send_message(message.chat.id, "Извините, но у вас закончились доступные сессии. Бот недоступен")
            return

    user_story = create_prompt(user_data, user_id)

    collection = get_dialogue_for_user(user_id, session_id)
    collection.append({'role': 'system', 'text': user_story})
    tokens: int = count_tokens_in_dialogue(collection)

    bot.send_message(message.chat.id, "Генерирую...")

    values = [user_id, 'system', user_story, time, tokens, session_id]
    insert_row(values)

    collection = get_dialogue_for_user(user_id, session_id)

    gpt_text, result_for_test = ask_gpt(collection)
    collection.append({'role': 'assistant', 'text': gpt_text})

    tokens: int = count_tokens_in_dialogue(collection)
    if is_limit_tokens(user_id, tokens):
        return

    values = [user_id, ]
    insert_row()


@bot.message_handler(commands=['all_tokens'])
def send_tokens(message):
    try:
        all_tokens = ''  # count_tokens_in_dialogue
        bot.send_message(message.chat.id, text=f'За все время использования бота\n'
                                               f'Израсходовано токенов - {all_tokens}',
                         reply_markup=create_keyboard(['new_story']))
    except Exception as e:
        bot.send_message(message.chat.id, f'Извините. произошла ошибка: {e}')


@bot.message_handler(commands=['end'])
def end(message):
    user_id = message.from_user.id
    if not is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        bot.send_message(message.chat.id, text="Кажется, вы еще не начали историю. Чтобы начать введи команду /begin",
                         reply_markup=create_keyboard(['/begin']))

    start_story(message, 'end')
    bot.send_message(message.chat.id, text="У нас получилась замечательная история. Приходи еще!",
                     reply_markup=create_keyboard(['/new_story']))


bot.infinity_polling()

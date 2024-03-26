# your_GPTassistant_bot
# -----------------------------------------------------ИМПОРТЫ----------------------------------------------------------
import telebot
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from telebot import types
import datetime
from gpt import *
from limitation import *

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
genres = ['Комедия', 'Приключения', 'Мистика']
main_characters = ['Буратино', 'Крош', 'Шерлок Хомс', 'Мисс Марпл', 'Аннабель', 'Волан де Морт']
locations = ['Фэнтези средневековый мир', 'Колониальный Марс', 'Волшебный магазин "Пятерочка"']

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
            'genre': None,
            'character': None,
            'location': None,
            'info': None,
            'state': None,
            'test_mode': None,
            'session_id': 0
        }

        create_db()
        logging.info('1 Создали бд')

        create_table(DB_TABLE_USERS_NAME)
        logging.info('2 Создали таблицу если ее нет')

        name_user = message.from_user.first_name
        logging.info("3 Отправка приветственного сообщения")
        bot.send_message(message.chat.id, text=f"Привет, {name_user}\n"
                                               f"Я бот-сценарист, который может помочь с созданием уникальных и "
                                               f"интересных историй. Напиши /new_story чтобы создать новую историю. "
                                               f"Чтобы закончить пиши /end.",
                         reply_markup=create_keyboard(['/new_story']))

    if message.text == '/help':
        logging.info("4 Отправка помощи")
        bot.send_message(message.chat.id, text='Запустите бот командой /start\n'
                                               'Начните новую историю командой /new_story\n'
                                               'Выберите жанр/главного героя/сеттинг\b'
                                               'Подождите пока история сгенерируется\n'
                                               'Напишите сообщение связанное с историей чтобы изменить продолжение '
                                               'истории и я продолжу вашу историю учитывая ваше сообщение или '
                                               'завершите историю введя команду /end',
                         reply_markup=create_keyboard(['/new_story']))


# ----------------------------------------------------ИСТОРИЯ-----------------------------------------------------------
@bot.message_handler(commands=['new_story'])
def story(message):
    user_id = message.from_user.id
    date = datetime.datetime.now()

    logging.info('5 Новая история')
    if is_limit_users():
        logging.info('6 количество пользователей превышено')
        bot.send_message(message.chat.id, "Извините, но количество пользователей превышено. Бот недоступен.")
        return

    if not is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        value = [user_id, '', '', date, 0, 0]
        insert_row(value)

    session_id = get_data_for_user(user_id, 'session_id', 'user_id', user_id)[0][0]
    session_id += 1
    user_data[user_id]['session_id'] = session_id

    try:
        session_id = get_data_for_user(user_id, 'session_id', 'user_id', user_id)[0][0]
        logging.info(f'7 session_id = {session_id}')

        if is_limit_sessions_id(user_id):
            if session_id == MAX_SESSIONS - 1:
                bot.send_message(message.chat.id, "Осталась 1 доступная сессия")
                logging.info("8 Сообщили о том, что сессии заканчиваются")
            else:
                logging.info("9 Сообщили о том, что сессии закончились")
                bot.send_message(message.chat.id, "Извините, но у вас закончились доступные сессии. Бот недоступен")
                return
    except TypeError:
        pass

    try:
        user_data[user_id]['state'] = "в истории"

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
        logging.info('10 Пользователь ввел не жанр')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(genres))
        bot.register_next_step_handler(message, choose_genre)
        return

    user_data[user_id]['genre'] = genre
    logging.info('11 Сохранили жанр в словарь')

    bot.send_message(message.chat.id, text='Хорошо, выберите главного героя',
                     reply_markup=create_keyboard(main_characters))
    bot.register_next_step_handler(message, choose_characters)


def choose_characters(message):
    user_id = message.from_user.id
    character = message.text

    if character not in main_characters:
        logging.info('12 Пользователь ввел не персонажа')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(main_characters))
        bot.register_next_step_handler(message, choose_characters)
        return

    user_data[user_id]['character'] = character
    logging.info('13 Сохранили персонажа в словарь')

    bot.send_message(message.chat.id, text='Отличный выбор, выберите сеттинг:\n'
                                           '1) Фэнтези средневековый мир - огромное королевство с магией.\n'
                                           '2) Колониальный Марс - люди колонизировали Марс и построили там города.\n'
                                           '3) Волшебный магазин "Пятерочка" -  место, где можно найти все, что угодно.'
                     ,
                     reply_markup=create_keyboard(locations))
    bot.register_next_step_handler(message, choose_locations)


def choose_locations(message):
    user_id = message.from_user.id
    location = message.text

    if location not in locations:
        logging.info('14 Пользователь ввел не сеттинг')
        bot.send_message(message.chat.id, text="Пожалуйста выберите один из предложенных вариантов",
                         reply_markup=create_keyboard(locations))
        bot.register_next_step_handler(message, choose_locations)
        return

    user_data[user_id]['location'] = location
    logging.info('15 Сохранили сеттинг в словарь')

    bot.send_message(message.chat.id, text="Супер! Получится крутая история, а чтобы она получилась еще круче можешь "
                                           "написать дополнительную информацию. Если хочешь уже начать пиши /begin",
                     reply_markup=create_keyboard(['/begin']))
    bot.register_next_step_handler(message, add_info)


def add_info(message):
    user_id = message.from_user.id
    info = message.text

    if info != '/begin':
        user_data[user_id]['info'] = info
        logging.info('16 Сохранили доп. инфо. в словарь')
        bot.send_message(message.chat.id, text='Отлично, вся информация будет учтена в истории. Чтобы начать введите '
                                               '/begin',
                         reply_markup=create_keyboard(['/begin']))
        return
    else:
        begin_story(message)


@bot.message_handler(commands=['begin'])
def begin_story(message):
    user_id = message.from_user.id

    try:
        if not user_data[user_id]['state']:
            logging.info("17 Пользователь не нажимал команду /new_story")
            bot.send_message(message.chat.id, text="Чтобы начать новую историю введите команду /new_story, и "
                                                   "пройдите опрос.",
                             reply_markup=create_keyboard(['/new_story']))
        elif not user_data[user_id]['genre']:
            logging.info("18 не выбрали жанр")
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали жанр, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(genres))
            bot.register_next_step_handler(message, choose_genre)

        elif not user_data[user_id]['character']:
            logging.info('19 не выбрали героя')
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали героя, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(main_characters))
            bot.register_next_step_handler(message, choose_characters)

        elif not user_data[user_id]['location']:
            logging.info('20 не выбрали сеттинг')
            bot.send_message(message.chat.id, text="Кажется, вы не выбрали сеттинг, пожалуйста выберите один из "
                                                   "предложенных вариантов.",
                             reply_markup=create_keyboard(locations))
            bot.register_next_step_handler(message, choose_locations)

    except KeyError:
        bot.send_message(message.chat.id, text="Чтобы начать введите команду /start",
                         reply_markup=create_keyboard(['/start']))

    get_story(message)


# ----------------------------------------------------ОБРАБОТКА ИСТОРИИ-------------------------------------------------
def get_story(message: types.Message):
    user_id = message.from_user.id
    time = datetime.datetime.now()

    session_id = user_data[user_id]['session_id']

    prompt = create_prompt(user_data, user_id)

    if user_data[user_id]['state'] == 'продолжение от пользователя':
        user_prompt = get_data_for_user(user_id, 'content', 'role', 'user')[0][0]
        if user_prompt == END_STORY:
            bot.register_next_step_handler(message, end)
        else:
            gpt_prompt = get_data_for_user(user_id, 'content', 'role', 'assistant')[0][0]
            prompt += f'{gpt_prompt}  {user_prompt} - {CONTINUE_STORY}'

    collection = [{'role': 'system', 'content': prompt}]

    tokens_system = count_tokens_in_dialogue(collection)

    bot.send_message(message.chat.id, "Генерирую...")

    logging.info('21 В таблице есть юзер, прибавляем к сессиям 1')

    if is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        if user_data[user_id]['state'] == 'продолжение от пользователя':
            tokens = get_tokens(user_id, session_id)
            tokens1 = tokens[0][0]
            tokens2 = tokens[1][0]
            tokens3 = tokens[2][0]
            token = tokens1 + tokens2 + tokens3

            if is_limit_tokens_in_session(user_id, token):
                bot.send_message(message.chat.id, 'Извините, но токены в данной сессии закончились. Чтобы начать новую '
                                                  'историю введите команду /new_story',
                                 reply_markup=create_keyboard(['/new_story']))
                return

    values = [user_id, 'system', prompt, time, tokens_system, session_id]
    insert_row(values)

    gpt_text = ask_gpt(collection)
    result_for_test = ask_gpt(collection)
    collection.append({'role': 'assistant', 'content': gpt_text})

    tokens_assistant = count_tokens_in_dialogue(collection)

    values = [user_id, 'assistant', gpt_text, time, tokens_assistant, session_id]
    insert_row(values)

    if not user_data[user_id]['test_mode']:
        bot.send_message(message.chat.id, gpt_text, reply_markup=create_keyboard(['/end']))
    else:
        bot.send_message(message.chat.id, result_for_test, reply_markup=create_keyboard(['/end']))
        bot.register_next_step_handler(message, end)
        return


@bot.message_handler(content_types=['text'])
def continuation(message: types.Message, mode='continue'):
    user_id = message.from_user.id
    user_message = message.text
    time = datetime.datetime.now()

    if not user_message:
        logging.info("Проверка на текстовое сообщение")
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение.")
        bot.register_next_step_handler(message, continuation)
        return

    try:
        if not user_data[user_id]['state']:
            logging.info("17 Пользователь не нажимал команду /new_story")
            bot.send_message(message.chat.id, text="Чтобы начать новую историю введите команду /new_story, и "
                                                   "пройдите опрос.",
                             reply_markup=create_keyboard(['/new_story']))
    except KeyError:
        bot.send_message(message.chat.id, text="Чтобы начать введите команду /start",
                         reply_markup=create_keyboard(['/start']))

    if user_message == '/end':
        user_message = END_STORY
        user_data[user_id]['test_mode'] = 'end'

    session_id = get_data_for_user(user_id, 'session_id', 'user_id', user_id)[0][0]

    collection = [{'role': 'user', 'content': user_message}]

    tokens_user = count_tokens_in_dialogue(collection)

    if is_limit_tokens(user_id, tokens_user):
        bot.send_message(message.chat.id, text='Ваше сообщение превышает лимит. Пожалуйста сократите сообщение и '
                                               'отправьте еще раз.')
        bot.register_next_step_handler(message, continuation)
        return

    values = [user_id, 'user', user_message, time, tokens_user, session_id]
    insert_row(values)
    try:
        user_data[user_id]['state'] = 'продолжение от пользователя'
    except KeyError:
        bot.send_message(message.chat.id, text="Чтобы начать введите команду /start",
                         reply_markup=create_keyboard(['/start']))

    get_story(message)
    # gpt_text = ask_gpt(collection)
    #
    # collection.append({'role': 'assistant', 'content': gpt_text})
    # print(collection, 'bot 4')
    #
    # tokens_assistant = count_tokens_in_dialogue(collection)
    #
    # values = [user_id, 'assistant', gpt_text, time, tokens_assistant, session_id]
    # insert_row(values)
    #
    # bot.send_message(message.chat.id, gpt_text)


# ---------------------------------------------------ТОКЕНЫ-------------------------------------------------------------
@bot.message_handler(commands=['all_tokens'])
def send_tokens(message):
    try:
        all_tokens = ''  # count_tokens_in_dialogue
        bot.send_message(message.chat.id, text=f'За все время использования бота\n'
                                               f'Израсходовано токенов - {all_tokens}',
                         reply_markup=create_keyboard(['new_story']))
    except Exception as e:
        bot.send_message(message.chat.id, f'Извините. произошла ошибка: {e}')


# ----------------------------------------------------КОНЕЦ-------------------------------------------------------------
@bot.message_handler(commands=['end'])
def end(message):
    user_id = message.from_user.id
    if not is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        bot.send_message(message.chat.id, text="Кажется, вы еще не начали историю. Чтобы начать введи команду /begin",
                         reply_markup=create_keyboard(['/begin']))

    continuation(message, '/end')
    bot.send_message(message.chat.id, text="У нас получилась замечательная история. Приходи еще!",
                     reply_markup=create_keyboard(['/new_story']))


bot.infinity_polling()

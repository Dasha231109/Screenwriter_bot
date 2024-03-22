from database import *


MAX_PROJECT_TOKENS = 15000  # макс. количество токенов на весь проект
MAX_USERS = 1  # макс. количество пользователей на весь проект
MAX_SESSIONS = 3  # макс. количество сессий у пользователя
MAX_TOKENS_IN_SESSION = 1000  # макс. количество токенов за сессию пользователя


def is_limit_users():
    result = distinct_data('user_id')
    count = 0
    for i in result:
        count += 1
    return count >= MAX_USERS


def is_limit_sessions_id(user_id):
    result = is_value_in_table(DB_TABLE_USERS_NAME, 'sessions_id', user_id)
    count = 0
    for i in result:
        count += 1
    return count >= MAX_SESSIONS




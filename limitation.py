import sqlite3

import requests
from config import *
from database import *


def is_limit_users():  # лимит юзеров
    users = distinct_data()
    count = 0
    for i in users:
        count += 1
    return count >= MAX_USERS


def is_limit_sessions_id(user_id):  # лимит сессий
    if not is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        return False

    session_id = get_data_for_user(user_id, "session_id")[0][0]

    return session_id == MAX_SESSIONS - 1 or session_id >= MAX_SESSIONS


def is_limit_tokens(user_id, tokens):
    if not is_value_in_table(DB_TABLE_USERS_NAME, 'user_id', user_id):
        return False

    return tokens > MAX_TOKENS


def count_tokens_in_dialogue(messages: sqlite3.Row):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
       "maxTokens": MAX_MODEL_TOKENS,
       "messages": []
    }

    for row in messages:
        print(messages, 'limi2')
        print(row, 'limi1')
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["content"]
            }
        )

    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
        ).json()["tokens"]
    )


if __name__ == '__main__':
    session = 0
    dialogue = [{'role': 'system', 'text': 'Ты помощник для решения задач по математике'}]

    while session < MAX_SESSIONS:
        user_text = input('Введи запрос к нейросети')
        dialogue.append({'role': 'system', 'text': user_text})

        c_tokens = count_tokens_in_dialogue(dialogue)

        if c_tokens > MAX_TOKENS_IN_SESSION:
            print('Превышен лимит токенов в сессии')
            break
        else:
            print('Все ок')

        result = ask_gpt(dialogue, '')
        print(result)

        dialogue.append({'role': 'assistant', 'text': result})
        session += 1

    print('Вы превысили лимит сессий')

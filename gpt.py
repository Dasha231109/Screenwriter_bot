import logging
import os

import requests
from config import *


# def create_new_token():
#     metadata = metadata_url
#     headers = {"Metadata-Flavor": "Google"}
#     token_dir = os.path.dirname(TOKEN_PATH)
#     response = requests.get(metadata_url, headers=headers)
#     return response.json()


def create_prompt(user_data, user_id):
    prompt = SYSTEM_PROMPT
    try:
        prompt += 'Комедия, Крош, Парк'# (f"\nНапиши начало истории в стиле {user_data[user_id]['genre']} "
        #            f"с главным героем {user_data[user_id]['character']}. "
        #            f"Вот начальный сеттинг: \n{user_data[user_id]['location']}. \n"
        #            "Начало должно быть коротким, 1-3 предложения.\n")

        logging.info('Создали промт на основе данных пользователя')
        if user_data[user_id]['info']:
            logging.info('Если юзер писал доп. инфо. также добавили в промт')
            prompt += (f"Также пользователь попросил учесть "
                       f"следующую дополнительную информацию: {user_data[user_id]['info']}. ")

        prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает\n '
        logging.info('Создали промт')
        return prompt
    except KeyError:
        return


def ask_gpt(collection, mode='continue'):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 40
        },
        "messages": []
    }

    for row in collection:
        content = row['content']

        if mode == "continue" and row['role'] == "user":
            content += '\n' + CONTINUE_STORY
        elif mode == "end" and row['role'] == "user":
            content += '\n' + END_STORY

        data["messages"].append(
            {
                "role": row["role"],
                "text": content
            }
        )

    try:
        response = requests.post(
            url,
            json=data,
            headers=headers
        )
        if response.status_code != 200:
            logging.debug(f"Response {response.json()} Status code:{response.status_code} Message {response.text}")
            res = f'Произошла ошибка. Статус код {response.status_code}. Подробности в журнале'
            return res
        res = response.json()["result"]["alternatives"][0]["message"]["text"]
    except Exception as e:
        logging.error(f'Ошибка {e}')
        res = 'Произошла непридвиденная ошибка'

    return res



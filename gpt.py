import logging
from limitation import *
import requests
from config import *


def create_prompt(current_choose, user_id):
    prompt = SYSTEM_PROMPT

    prompt += (f"\nНапиши начало истории в стиле {current_choose[user_id]['genre']} "
               f"с главным героем {current_choose[user_id]['character']}. "
               f"Вот начальный сеттинг: \n{current_choose[user_id]['location']}. \n"
               "Начало должно быть коротким, 1-3 предложения.\n")

    if current_choose[user_id]['info']:
        prompt += (f"Также пользователь попросил учесть "
                   f"следующую дополнительную информацию: {current_choose[user_id]['info']} ")

    prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает'

    return prompt


def ask_gpt(collection, user_content):
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
            "maxTokens": MAX_TOKENS_IN_SESSION
        },
        "messages": [
            {'role': 'system', 'text': user_content['system_content']},
            {'role': 'user', 'text': user_content['user_content']},
            {"role": "assistant", "content": user_content['assistant_content']}
        ]
    }

    for row in collection:
        data["messages"].append(
            {
                "role": row["role"],
                "text": row["text"]
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


if __name__ == '__main__':
    session = 0
    dialogue = [{'role': 'system', 'text': 'Ты помощник для решения задач по математике'}]

    while session < MAX_SESSIONS:
        user_text = input('Введи запрос к нейросети')
        dialogue.append({'role': 'system', 'text': user_text})

        tokens = count_tokens_in_dialogue(dialogue)

        if tokens > MAX_TOKENS_IN_SESSION:
            print('Превышен лимит токенов в сессии')
            break
        else:
            print('Все ок')

        result = ask_gpt(dialogue)
        print(result)

        dialogue.append({'role': 'assistant', 'text': result})
        session += 1

    print('Вы превысили лимит сессий')

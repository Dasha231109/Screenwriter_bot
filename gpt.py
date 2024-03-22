import requests


def ask_gpt(text):
    iam_token = ('t1.9euelZqVzMiZkZfHk4yJkJKVjYqNi-3rnpWalouPmsiKkJDOjpWSmsyKjI_l8_dAbgpQ'
                 '-e8SYiwu_N3z9wAdCFD57xJiLC78zef1656VmsaSks6SxonJzpqZzMyOjIzO7_zF656VmsaSks6SxonJzpqZzMyOjIzOveuelZqUl'
                 '8-KnpLMm82OjMaYnJGak7XehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.ddoXv7mczFMZpVjK_-EYj_Y3Wd6_mod5r'
                 'GoXuT4E6OdVAjrhymCBQKltN9fOcSWAeSz3_lcnIYKrKp0j5ai0Cw')
    folder_id = 'b1gt97gj64dtkbtnaf0a'

    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 50
        },
        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }

    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)

    if response.status_code == 200:
        text = response.json()["result"]["alternatives"][0]["message"]["text"]
        return text
    else:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                {response.status_code}, {response.text}
            )
        )


query = "Расскажи, какие бывают котики"
print(ask_gpt(query))

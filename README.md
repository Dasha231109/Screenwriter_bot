# Бот-сценарист  
 
## Бот состоит из четырех модулей: 
- bot  
- gpt 
- database 
- config 
 
## Путь пользователя 
1) Приветственное сообщение, инструкция использования по команде /start. Пользователь вводит /new_story 
2) Оповещение о кол-во токенов. "Выберите жанр" и кнопки. 
3) "Выберите главного героя" и кнопки 
4) "Выберите сеттинг", небольшая информация и кнопки 
5) Предложение о вводе доп. информации. Пользователь вводит /begin 
6) Оповещение о кол-во сессий и если они заканчиваются/закончились 
7) Оповещение если токены заканчиваются/закончились 
8) История от gpt. Продолжение истории от пользователя. Пока не закончатся сессии или пользователь не введет /end  
9) Если пользователь ввел /all_tokens, выводится затраченное кол-во токенов   

# Шаг 1. Заходим на сервер используя команду (указать свой IP и место расположения ключа)
# ssh -i C:\Users\ПК\Documents\hf7Gjgk458HG6gapcM student@158.160.141.223
# Шаг 2. Получение IAM-токена
# curl -sf -H Metadata-Flavor:Google 169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token

# TG-VK Translator
Транслятор новостей Telegram-канала в VK.

## How it works
В Telegram через Client API прослушивается канал. Как только появляется сообщение, оно обрабатывается, и Бот в VK отправляет его пользователям, которые подписались на рассылку (т.е. написали Боту "Подписка" и попали в БД).

Таким образом, при появлении новостей в Telegram-канале юзерам в VK будет присылаться личное сообщение от Бота.

## Features
Поддерживается следующий функционал:
- текстовые сообщения
- сообщения с фотографиями
- сообщения с документами
- если сообщение любого из типов выше было отредактировано, бот отправит его повторно, указывая, что сообщение было изменено
- указывается автор сообщения и время отправления/редактирования

## Getting started
1. Клонировать репозиторий и установить зависимости:
``` 
git clone https://github.com/artnovopolsky/from-telegram-to-vk.git
cd from-telegram-to-vk
pip install -r requirements.txt 
```
2. Заполнить ``` config.py ```. Для этого нужно:
    
    - Получить свой API_ID и API_HASH Telegram [здесь](https://my.telegram.org/apps).
    - Создать группу в VK и настроить бота (сгенерировать ключ доступа, включить Long Pool API)
    - Узнать ID подслушиваемого Telegram-канала [здесь](https://www.telegram.me/getmyid_bot).
    
3. Запустить (в первый раз понадобится ввести номер телефона и код подтверждения для авторизации Telegram-клиента):
   
``` python telegram_client.py & python vk_bot.py ```

4. Написать Боту в VK ``` Подписка``` и ждать обновлений Telegram-канала :)

## Libraries used

- vk_api - [документация](https://vk-api.readthedocs.io/en/latest/)
- pyrogram - [документация](https://docs.pyrogram.org/)

## Example
Пример работы:

![](/home/artnovopolsky/Изображения/tgvktranslator.jpeg)

import config

from telethon import TelegramClient, events
from vk_api.utils import get_random_id
from vk_bot import VKBot

client = TelegramClient('kispython', config.TG_API_ID, config.TG_API_HASH)  # Инициализация клиента TG


def make_message_header(author, time):
    """ Создание заголовка сообщения. """

    # TODO: правильное отображение даты (+3 часа)
    emoji = '🐍'
    time = time.strftime("%H:%M:%S")
    return f'{emoji} {author} ({time})\n\n'


def get_message_for_vk(event):
    """ Создание сообщения для """
    author = event.message.post_author
    time = event.message.date
    message_text = event.message.message
    message_header = make_message_header(author, time)
    message = message_header + message_text
    return message


@client.on(events.NewMessage(chats=config.CHANNEL_NAME))
async def new_message_handler(event):
    """ Обработчик нового сообщения в канале. """

    message = get_message_for_vk(event)

    # Если сообщение содержит фото
    if event.message.photo:
        file_path = await event.message.download_media(config.get_unique_filename())
        upload = VKBot.upload_photo(VKBot.upload, file_path)
        users = VKBot.db.get_subscribers()
        VKBot.send_message_with_photo(VKBot.vk, message, users, *upload)

    # Если фото содержит документ
    elif event.message.document:
        filename = event.message.document.attributes[0].file_name
        file_path = await event.message.download_media(config.get_unique_filename())
        users = VKBot.db.get_subscribers()

        # Загружаем документ на сервер VK только для одного пользователя, а дальше отправляем его всем
        attachments = VKBot.upload_document(VKBot.upload, file_path, users[0], filename)
        VKBot.send_message_with_document(VKBot.vk, message, users, *attachments)

    # Если сообщение содержит только текст
    else:
        users = VKBot.db.get_subscribers()  # Получаем список из кортежей с id

        # Делаем данные users валидными для отправления запроса (id должны быть строками)
        users_id = [str(user[0]) for user in users]

        # Разбиваем пользователей на группы, чтобы не превысить лимит запросов в секунду
        user_groups = VKBot.group(users_id, 80)
        for user_group in user_groups:
            VKBot.vk.messages.send(user_ids=','.join(user_group), message=message, random_id=get_random_id())


@client.on(events.MessageEdited(chats=config.CHANNEL_NAME))
async def edited_message_handler(event):
    """ Обработчик отредактированного сообщения в канале. """
    pass

with client:
    client.run_until_disconnected()

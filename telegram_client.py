from datetime import datetime
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
        for user in users:
            VKBot.send_message_with_photo(VKBot.vk, message, user, *upload)

    # Если фото содержит документ
    elif event.message.document:
        filename = event.message.document.attributes[0].file_name
        print(filename)
        file_path = await event.message.download_media(config.get_unique_filename())
        users = VKBot.db.get_subscribers()
        for user in users:
            upload = VKBot.upload_document(VKBot.upload, file_path, user, filename)
            VKBot.send_message_with_document(VKBot.vk, message, user, *upload)

    # Если сообщение содержит только текст
    else:
        users = VKBot.db.get_subscribers()
        for user in users:
            VKBot.vk.messages.send(user_id=user, message=message, random_id=get_random_id())


@client.on(events.MessageEdited(chats=config.CHANNEL_NAME))
async def edited_message_handler(event):
    """ Обработчик отредактированного сообщения в канале. """
    pass

with client:
    client.run_until_disconnected()

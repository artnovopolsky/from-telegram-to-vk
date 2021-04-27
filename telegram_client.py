from datetime import datetime, timedelta
from pyrogram import Client, filters

import config
from vk_bot import VKBot


tg_client = Client("kispython-translator", api_id=config.TG_API_ID, api_hash=config.TG_API_HASH)


def make_message_header(author, msg_time, edit=False):
    """ Создание заголовка сообщения для VK. """

    emoji = '🐍'
    msg_time = datetime.utcfromtimestamp(msg_time) + timedelta(hours=3)  # Для отображения Московского времени
    msg_time = msg_time.strftime("%H:%M:%S")
    if not edit:
        return f'{emoji} {author} ({msg_time})\n\n'
    else:
        return f'{emoji} {author} (изменено в {msg_time})\n\n'


def get_message_for_vk(message, edit=False, media=False):
    """ Создание сообщения для VK. """

    author = message.author_signature
    message_text = message.text if not media else message.caption

    if not edit:
        msg_time = message.date
        message_header = make_message_header(author, msg_time)
    else:
        msg_time = message.edit_date
        message_header = make_message_header(author, msg_time, edit=True)

    message = message_header + message_text if message_text is not None else message_header

    return message


@tg_client.on_message(filters.chat(chats=config.TG_CHAT_ID) & filters.text)
def message_handler(client, message):
    """ Обработчик текстовых сообщений в канале. """

    if message.edit_date is not None:
        msg = get_message_for_vk(message, edit=True)
    else:
        msg = get_message_for_vk(message)

    vk_bot.send_text_message(msg)


@tg_client.on_message(filters.chat(chats=config.TG_CHAT_ID) & (filters.photo | filters.document))
def media_message_handler(client, message):
    """ Обработчик сообщений с медиа в канале. """

    if message.edit_date is not None:
        msg = get_message_for_vk(message, edit=True, media=True)
    else:
        msg = get_message_for_vk(message, media=True)

    # Если сообщение содержит фото
    if message.photo:
        file_path = message.download()
        vk_bot.send_message_with_photo(msg, file_path)

    # Если сообщение содержит документ
    elif message.document:
        file_name = message.document.file_name
        file_path = message.download()
        vk_bot.send_message_with_document(msg, file_path, file_name)


if __name__ == '__main__':
    vk_bot = VKBot()
    tg_client.run()

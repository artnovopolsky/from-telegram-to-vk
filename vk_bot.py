import time

import vk_api
from vk_api.upload import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

import config
from database import Database


class VKBot:

    vk_session = vk_api.VkApi(token=config.VK_GROUP_TOKEN)
    vk = vk_session.get_api()
    upload = VkUpload(vk)
    long_poll = VkBotLongPoll(vk_session, config.VK_GROUP_ID)
    db = Database('users.db')  # Инициализация соединения с БД

    def incoming_message_handler(self):
        """ Обработчик входящих сообщений бота. """

        # Слушаем события бота
        for event in self.long_poll.listen():

            # Если пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:

                # Если это стартовое сообщение
                if event.object.message['text'].lower() == 'Подписка'.lower():
                    # Сохраняем ID пользователя в БД
                    user_id = event.object.message['from_id']
                    if not self.db.subscriber_exists(user_id):
                        self.db.add_subscriber(user_id)
                        # Отправляем справочное сообщение
                        memo_message = 'Подписка успешно оформлена. Как только появится новая информация, я дам знать. ' \
                                       'На связи! 🤓\n\nЕсли захочешь отписаться от рассылки, напиши мне "Отписка".'
                        self.vk.messages.send(user_id=user_id, message=memo_message, random_id=get_random_id())
                    # Если пользователь уже подписан
                    else:
                        message = 'Ты уже подписан на рассылку. Как только будут новости, я отпишу :)'
                        self.vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())

                # Если это сообщение об отписке
                elif event.object.message['text'].lower() == 'Отписка'.lower():
                    # Удаляем ID пользователя из БД
                    user_id = event.object.message['from_id']
                    if self.db.subscriber_exists(user_id):
                        self.db.remove_subscriber(user_id)
                        # Отправляем финальное сообщение
                        final_message = 'Подписка успешно отменена. ' \
                                        'Если захочешь возобновить подписку, просто напиши мне "Подписка".\n\n' \
                                        'Буду ждать! 🥺'
                        self.vk.messages.send(user_id=user_id, message=final_message, random_id=get_random_id())
                    # Если пользователь ещё не подписан
                    else:
                        message = 'Ты ещё не подписан на рассылку, чтобы отписываться :)\n' \
                                  'Для того, чтобы оформить подписку, напиши мне "Подписка".'
                        self.vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())

                # Если это любое другое сообщение
                else:
                    # Сначала проверяем, есть ли ID пользователя в БД
                    user_id = event.object.message['from_id']
                    # Если пользователь уже подписан на рассылку
                    if self.db.subscriber_exists(user_id):
                        message = 'Доступны только команды "Подписка" и "Отписка".'
                        self.vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())
                    # Если пользователь ещё не подписан на рассылку
                    else:
                        message = 'Доступны только команды "Подписка" для оформления подписки и ' \
                                  '"Отписка" для отмены подписки.'
                        self.vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())

    def check_permission_to_send_messages(self, users):
        """
        Проверка на то, разрешил ли пользователь писать ему сообщения.
        Если нет разрешения, но есть подписка, просто исключаем юзера из рассылки.

        Таким образом, когда пользователь снова разрешит сообщения, он будет их получать.
        """
        for user in users:
            permission = self.vk.messages.is_messages_from_group_allowed(group_id=config.VK_GROUP_ID, user_id=user)
            if permission['is_allowed'] == 0:
                users.remove(user)
            time.sleep(0.3)  # Спим для того, чтобы точно не превысить лимит запросов в VK :)
        return users

    def group(self, users, n=50):
        """ Группировка списка юзеров по n человек для эффективной рассылки. """
        res_users = self.check_permission_to_send_messages(users)
        return [res_users[i:i+n] for i in range(0, len(res_users), n)]

    @staticmethod
    def make_user_ids_valid(users):
        """ Валидация users для отправления запроса (id должны быть строками). """
        user_ids = [str(user[0]) for user in users]
        return user_ids

    def send_text_message(self, msg):
        """ Отправление текстового сообщения в VK. """

        users = self.db.get_subscribers()  # Получаем список из кортежей с id
        user_ids = self.make_user_ids_valid(users)

        # Разбиваем пользователей на группы, чтобы не превысить лимит запросов в секунду
        user_groups = self.group(user_ids, 80)
        for user_group in user_groups:
            self.vk.messages.send(user_ids=','.join(user_group), message=msg, random_id=get_random_id())
            time.sleep(0.5)  # Спим для того, чтобы точно не превысить лимит запросов в VK :)

    def upload_photo(self, path):
        """ Загрузка фото на сервер VK. """

        response = self.upload.photo_messages(path)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        return owner_id, photo_id, access_key

    def send_message_with_photo(self, msg, file_path):
        """ Отправление сообщения с фото в VK. """

        owner_id, photo_id, access_key = self.upload_photo(file_path)
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'

        user_ids = self.db.get_subscribers()  # Получаем список из кортежей с id
        users = self.make_user_ids_valid(user_ids)

        # Разбиваем пользователей на группы, чтобы не превысить лимит запросов в секунду
        user_groups = self.group(users, 80)
        for user_group in user_groups:
            self.vk.messages.send(user_ids=','.join(user_group), message=msg,
                                  attachment=attachment, random_id=get_random_id())
            time.sleep(0.5)  # Спим для того, чтобы точно не превысить лимит запросов в VK :)

    def upload_document(self, path, peer_id, file_name):
        """ Загрузка документа на сервер VK. """

        response = self.upload.document_message(doc=path, peer_id=peer_id, title=file_name)
        owner_id = response['doc']['owner_id']
        doc_id = response['doc']['id']
        return owner_id, doc_id

    def send_message_with_document(self, message, file_path, file_name):
        """ Отправление сообщения с документом в VK. """

        user_ids = self.db.get_subscribers()  # Получаем список из кортежей с id
        users = VKBot.make_user_ids_valid(user_ids)

        owner_id, doc_id = self.upload_document(file_path, user_ids[0], file_name)
        attachments = [f'doc{owner_id}_{doc_id}', ]

        # Разбиваем пользователей на группы, чтобы не превысить лимит запросов в секунду
        user_groups = self.group(users, 80)
        for user_group in user_groups:
            self.vk.messages.send(user_ids=','.join(user_group), message=message, attachment=','.join(attachments),
                                  random_id=get_random_id())
            time.sleep(0.5)  # Спим для того, чтобы точно не превысить лимит запросов в VK :)


if __name__ == '__main__':
    bot = VKBot()
    bot.incoming_message_handler()

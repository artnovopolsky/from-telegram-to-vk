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
    longpoll = VkBotLongPoll(vk_session, config.VK_GROUP_ID)
    db = Database('users.db')  # Инициализация соединения с БД

    def incoming_message_handler(self):
        """ Обработчик входящих сообщений бота. """

        # Слушаем события бота
        for event in self.longpoll.listen():

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

    @staticmethod
    def upload_photo(upload, path):
        """ Загрузка фото на сервер VK. """
        response = upload.photo_messages(path)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        return owner_id, photo_id, access_key

    @staticmethod
    def send_message_with_photo(vk, message, user_id, owner_id, photo_id, access_key):
        """ Отправление сообщения с фото в VK. """
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        vk.messages.send(user_id=user_id, message=message, attachment=attachment, random_id=get_random_id())

    @staticmethod
    def upload_document(upload, path, peer_id, filename):
        """ Загрузка документа на сервер VK. """
        response = upload.document_message(doc=path, peer_id=peer_id, title=filename)
        owner_id = response['doc']['owner_id']
        doc_id = response['doc']['id']
        return owner_id, doc_id

    @staticmethod
    def send_message_with_document(vk, message, user_id, owner_id, doc_id):
        """ Отправление сообщения с документом в VK. """
        attachments = [f'doc{owner_id}_{doc_id}', ]
        vk.messages.send(user_id=user_id, message=message, attachment=','.join(attachments), random_id=get_random_id())


if __name__ == '__main__':
    VKBot().incoming_message_handler()

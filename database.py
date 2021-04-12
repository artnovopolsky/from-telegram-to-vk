import sqlite3


class Database:

    def __init__(self, database):
        """ Подключение к БД и сохранение курсора соединения. """
        self.connection = sqlite3.connect(database, timeout=10)
        self.cursor = self.connection.cursor()

    def get_subscribers(self):
        """ Получение всех активных подписчиков бота. """
        with self.connection:
            return self.cursor.execute("SELECT * FROM subscriptions;").fetchall()

    def subscriber_exists(self, user_id):
        """ Проверка, есть ли уже юзер в базе. """
        with self.connection:
            result = self.cursor.execute("SELECT * FROM subscriptions WHERE id = ?;", (user_id, )).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id):
        """ Добавление нового подписчика. """
        with self.connection:
            self.cursor.execute("INSERT INTO subscriptions (id) VALUES (?);", (user_id, ))

    def remove_subscriber(self, user_id):
        """ Удаление юзера, отменившего подписку. """
        with self.connection:
            self.cursor.execute("DELETE from subscriptions where id = ?;", (user_id, ))

    def close(self):
        """ Закрытие соединения с БД. """
        self.cursor.close()
        self.connection.close()

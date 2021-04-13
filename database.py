import sqlite3


class Database:

    def __init__(self, database='users'):
        """ Инициализация и подключение к БД. """

        self.database = database
        self.connection = sqlite3.connect(database)
        with self.connection:
            self.connection.execute("CREATE TABLE IF NOT EXISTS subscriptions(user_id INT PRIMARY KEY);")
        self.connection.close()

    def get_subscribers(self):
        """ Получение всех активных подписчиков бота. """

        self.connection = sqlite3.connect(self.database)
        with self.connection:
            result = self.connection.execute("SELECT * FROM subscriptions;").fetchall()
        self.connection.close()
        return result

    def subscriber_exists(self, user_id):
        """ Проверка, есть ли уже юзер в базе. """

        self.connection = sqlite3.connect(self.database)
        with self.connection:
            result = self.connection.execute("SELECT * FROM subscriptions WHERE user_id = ?;", (user_id, )).fetchall()
        self.connection.close()
        return bool(len(result))

    def add_subscriber(self, user_id):
        """ Добавление нового подписчика. """

        self.connection = sqlite3.connect(self.database)
        with self.connection:
            self.connection.execute("INSERT INTO subscriptions (user_id) VALUES (?);", (user_id, ))
        self.connection.close()

    def remove_subscriber(self, user_id):
        """ Удаление юзера, отменившего подписку. """

        self.connection = sqlite3.connect(self.database)
        with self.connection:
            self.connection.execute("DELETE from subscriptions where user_id = ?;", (user_id, ))
        self.connection.close()

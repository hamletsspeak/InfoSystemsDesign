import mysql.connector

class DatabaseConnectionSingleton:
    """Класс-одиночка для управления подключением к базе данных."""
    
    _instance = None

    def __new__(cls, db_config):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionSingleton, cls).__new__(cls)
            cls._instance._initialize(db_config)
        return cls._instance

    def _initialize(self, db_config):
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        """Выполнение SQL-запроса и возврат результатов."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        """Выполнение SQL-команды на изменение данных."""
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class ClientEntityRepDB:
    """Класс для работы с таблицей клиентов через адаптер DatabaseConnectionSingleton."""

    def __init__(self, db_config):
        # Используем адаптер для подключения к базе данных через Singleton
        self.db = DatabaseConnectionSingleton(db_config)

    def get_by_id(self, client_id):
        """Получить объект Client по ID."""
        query = "SELECT * FROM client WHERE id = %s"
        results = self.db.execute_query(query, (client_id,))
        return results[0] if results else None

    def get_k_n_short_list(self, k, n):
        """Получить список k по счёту n объектов."""
        offset = (k - 1) * n
        query = f"SELECT * FROM client ORDER BY id LIMIT {n} OFFSET {offset}"
        return self.db.execute_query(query)

    def add_client(self, client_data):
        """Добавить клиента в базу данных."""
        query = "INSERT INTO client (name, email, phone) VALUES (%s, %s, %s)"
        params = (client_data['name'], client_data['email'], client_data['phone'])
        return self.db.execute_update(query, params)

    def update_client_by_id(self, client_id, client_data):
        """Обновить данные клиента по ID."""
        query = "UPDATE client SET name = %s, email = %s, phone = %s WHERE id = %s"
        params = (client_data['name'], client_data['email'], client_data['phone'], client_id)
        self.db.execute_update(query, params)

    def delete_client_by_id(self, client_id):
        """Удалить клиента по ID."""
        query = "DELETE FROM client WHERE id = %s"
        self.db.execute_update(query, (client_id,))

    def get_count(self):
        """Получить количество клиентов."""
        query = "SELECT COUNT(*) AS count FROM client"
        result = self.db.execute_query(query)
        return result[0]['count'] if result else 0

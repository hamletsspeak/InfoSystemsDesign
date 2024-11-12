import mysql.connector

class DatabaseConnectionSingleton:
    """Класс-одиночка для управления подключением к базе данных."""
    
    _instance = None  # Хранение единственного экземпляра класса

    def __new__(cls, db_config):
        """Создание единственного экземпляра DatabaseConnectionSingleton."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionSingleton, cls).__new__(cls)
            cls._instance._initialize(db_config)
        return cls._instance

    def _initialize(self, db_config):
        """Инициализация подключения к базе данных."""
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        """Выполнение SQL-запроса с параметрами и возврат результатов."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        """Выполнение SQL-команды на обновление, вставку или удаление данных."""
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def __del__(self):
        """Закрытие подключения при уничтожении объекта."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class ClientEntity_rep_DB:
    """Класс для работы с таблицей клиентов через адаптер DatabaseConnectionSingleton."""

    def __init__(self, db_config):
        # Подключаемся через Singleton
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
        """Добавить клиента в список после валидации данных."""
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


# Настройки базы данных
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Пример использования:
client_db = ClientEntity_rep_DB(db_config)

# Пример 1: Добавление нового клиента
new_client = {
    'name': 'Jane Doe',
    'email': 'janedoe@example.com',
    'phone': '555-1234'
}
new_client_id = client_db.add_client(new_client)
print(f"Добавлен клиент с ID: {new_client_id}")

# Пример 2: Получение клиента по ID
client = client_db.get_by_id(new_client_id)
print(f"Полученный клиент: {client}")

# Пример 3: Получение списка клиентов (первые 5 клиентов, начиная с первой страницы)
clients_list = client_db.get_k_n_short_list(1, 5)
print("Список клиентов (первые 5):")
for c in clients_list:
    print(c)

# Пример 4: Обновление данных клиента по ID
updated_data = {
    'name': 'Jane Smith',
    'email': 'janesmith@example.com',
    'phone': '555-5678'
}
client_db.update_client_by_id(new_client_id, updated_data)
print(f"Клиент с ID {new_client_id} обновлен.")

# Пример 5: Удаление клиента по ID
client_db.delete_client_by_id(new_client_id)
print(f"Клиент с ID {new_client_id} удален.")

# Пример 6: Получение общего количества клиентов
total_clients = client_db.get_count()
print(f"Общее количество клиентов: {total_clients}")

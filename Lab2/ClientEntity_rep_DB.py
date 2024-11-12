import mysql.connector


class ClientEntity_rep_DB:
    def __init__(self, db_config):
        # Устанавливаем соединение с базой данных
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor(dictionary=True)

    @staticmethod
    def validate_string(value, field_name, max_length=None):
        if not isinstance(value, str) or (max_length and len(value) > max_length):
            raise ValueError(f"{field_name} must be a string with max length {max_length}")
        return value

    @staticmethod
    def validate_email(value):
        if '@' not in value or '.' not in value:
            raise ValueError("Invalid email address")
        return value

    def get_by_id(self, client_id):
        # Получить объект Client по ID
        query = "SELECT * FROM client WHERE id = %s"
        self.cursor.execute(query, (client_id,))
        return self.cursor.fetchone()

    def get_k_n_short_list(self, k, n):
        # Получить k по счёту n объектов
        offset = (k - 1) * n
        query = f"SELECT * FROM client ORDER BY id LIMIT {n} OFFSET {offset}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_client(self, client_data):
        # Добавить клиента в список после валидации данных
        name = self.validate_string(client_data['name'], 'Name', max_length=100)
        email = self.validate_email(client_data['email'])
        phone = self.validate_string(client_data['phone'], 'Phone', max_length=15)
        
        query = "INSERT INTO client (name, email, phone) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (name, email, phone))
        self.connection.commit()
        return self.cursor.lastrowid

    def update_client_by_id(self, client_id, client_data):
        # Обновить данные клиента по ID с валидацией
        name = self.validate_string(client_data['name'], 'Name', max_length=100)
        email = self.validate_email(client_data['email'])
        phone = self.validate_string(client_data['phone'], 'Phone', max_length=15)
        
        query = "UPDATE client SET name = %s, email = %s, phone = %s WHERE id = %s"
        self.cursor.execute(query, (name, email, phone, client_id))
        self.connection.commit()

    def delete_client_by_id(self, client_id):
        # Удалить клиента по ID
        query = "DELETE FROM client WHERE id = %s"
        self.cursor.execute(query, (client_id,))
        self.connection.commit()

    def get_count(self):
        # Получить количество клиентов
        query = "SELECT COUNT(*) AS count FROM client"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result['count'] if result else 0

    def __del__(self):
        # Закрываем соединение при уничтожении объекта
        self.cursor.close()
        self.connection.close()

db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Подключение к базе данных
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

import sqlite3

class ClientEntity_rep_DB:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS client (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT
            )
        ''')
        self.connection.commit()

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
        query = "SELECT * FROM client WHERE id = ?"
        self.cursor.execute(query, (client_id,))
        return dict(self.cursor.fetchone())

    def get_k_n_short_list(self, k, n):
        offset = (k - 1) * n
        query = f"SELECT * FROM client ORDER BY id LIMIT ? OFFSET ?"
        self.cursor.execute(query, (n, offset))
        return [dict(row) for row in self.cursor.fetchall()]

    def add_client(self, client_data):
        name = self.validate_string(client_data['name'], 'Name', max_length=100)
        email = self.validate_email(client_data['email'])
        phone = self.validate_string(client_data['phone'], 'Phone', max_length=15)
        
        query = "INSERT INTO client (name, email, phone) VALUES (?, ?, ?)"
        self.cursor.execute(query, (name, email, phone))
        self.connection.commit()
        return self.cursor.lastrowid

    def update_client_by_id(self, client_id, client_data):
        name = self.validate_string(client_data['name'], 'Name', max_length=100)
        email = self.validate_email(client_data['email'])
        phone = self.validate_string(client_data['phone'], 'Phone', max_length=15)
        
        query = "UPDATE client SET name = ?, email = ?, phone = ? WHERE id = ?"
        self.cursor.execute(query, (name, email, phone, client_id))
        self.connection.commit()

    def delete_client_by_id(self, client_id):
        query = "DELETE FROM client WHERE id = ?"
        self.cursor.execute(query, (client_id,))
        self.connection.commit()

    def get_count(self):
        query = "SELECT COUNT(*) AS count FROM client"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

db_path = 'clients.db'
client_db = ClientEntity_rep_DB(db_path)

new_client = {
    'name': 'Jane Doe',
    'email': 'janedoe@example.com',
    'phone': '555-1234'
}
new_client_id = client_db.add_client(new_client)
print(f"Добавлен клиент с ID: {new_client_id}")

client = client_db.get_by_id(new_client_id)
print(f"Полученный клиент: {client}")

clients_list = client_db.get_k_n_short_list(1, 5)
print("Список клиентов (первые 5):")
for c in clients_list:
    print(c)

updated_data = {
    'name': 'Jane Smith',
    'email': 'janesmith@example.com',
    'phone': '555-5678'
}
client_db.update_client_by_id(new_client_id, updated_data)
print(f"Клиент с ID {new_client_id} обновлен.")

client_db.delete_client_by_id(new_client_id)
print(f"Клиент с ID {new_client_id} удален.")

total_clients = client_db.get_count()
print(f"Общее количество клиентов: {total_clients}")

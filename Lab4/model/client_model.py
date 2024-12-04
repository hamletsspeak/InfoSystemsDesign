import sqlite3

class ClientModel:
    def __init__(self, db_name="C:/Users/Гамлет/Desktop/InfoSysDesign/pawnshop.db"):
        self.conn = sqlite3.connect(db_name)

    def _create_table(self):
        """Создание таблицы, если её нет."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                inn TEXT NOT NULL,
                birth_date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def get_all_clients(self):
        """Получение списка всех клиентов."""
        cursor = self.conn.execute("SELECT id, fio, phone FROM clients")
        return cursor.fetchall()

    def get_client_by_id(self, client_id):
        """Получение данных клиента по ID."""
        cursor = self.conn.execute(
            "SELECT id, fio, phone, address, inn, birth_date FROM clients WHERE id = ?",
            (client_id,)
        )
        return cursor.fetchone()

    def add_client(self, client_data):
        """Добавление клиента."""
        self.conn.execute("""
            INSERT INTO clients (fio, phone, address, inn, birth_date)
            VALUES (?, ?, ?, ?, ?)
        """, (client_data['fio'], client_data['phone'], client_data['address'],
              client_data['inn'], client_data['birth_date']))
        self.conn.commit()

    def delete_client(self, client_id):
        """Удаление клиента."""
        self.conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        self.conn.commit()
        
    def update_client(self, client_id, client_data):
        """Обновление данных клиента."""
        self.conn.execute("""
            UPDATE clients
            SET fio = ?, phone = ?, address = ?, inn = ?, birth_date = ?
            WHERE id = ?
        """, (client_data['fio'], client_data['phone'], client_data['address'],
            client_data['inn'], client_data['birth_date'], client_id))
        self.conn.commit()
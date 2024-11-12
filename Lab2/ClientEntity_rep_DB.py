import mysql.connector
from functools import wraps

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


def with_filter_and_sort(func):
    """Декоратор для добавления фильтрации и сортировки в методы get_k_n_short_list и get_count."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Получаем параметры фильтрации и сортировки, если они переданы
        filters = kwargs.get('filters', {})
        sort_by = kwargs.get('sort_by')
        
        # Формируем условия WHERE для фильтрации
        filter_conditions = []
        filter_values = []
        for field, value in filters.items():
            filter_conditions.append(f"{field} = %s")
            filter_values.append(value)
        where_clause = f"WHERE {' AND '.join(filter_conditions)}" if filter_conditions else ""
        
        # Формируем часть ORDER BY для сортировки
        order_clause = f"ORDER BY {sort_by}" if sort_by else ""
        
        # Вызываем исходный метод с добавлением условий
        return func(self, *args, where_clause=where_clause, filter_values=filter_values, order_clause=order_clause)
    
    return wrapper


class ClientEntityRepDB:
    """Класс для работы с таблицей клиентов через адаптер DatabaseConnectionSingleton."""

    def __init__(self, db_config):
        self.db = DatabaseConnectionSingleton(db_config)

    @with_filter_and_sort
    def get_k_n_short_list(self, k, n, where_clause="", filter_values=None, order_clause=""):
        """Получить список k по счёту n объектов с фильтрацией и сортировкой."""
        filter_values = filter_values or []
        offset = (k - 1) * n
        query = f"SELECT * FROM client {where_clause} {order_clause} LIMIT %s OFFSET %s"
        return self.db.execute_query(query, filter_values + [n, offset])

    @with_filter_and_sort
    def get_count(self, where_clause="", filter_values=None, order_clause=""):
        """Получить количество клиентов с фильтрацией."""
        filter_values = filter_values or []
        query = f"SELECT COUNT(*) AS count FROM client {where_clause}"
        result = self.db.execute_query(query, filter_values)
        return result[0]['count'] if result else 0

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

# Настройки базы данных
db_config = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password',
    'database': 'database_name'
}

# Пример использования:
client_db = ClientEntityRepDB(db_config)

# Пример 1: Получение списка клиентов с фильтрацией и сортировкой
filtered_clients = client_db.get_k_n_short_list(
    1, 10,
    filters={'name': 'Alice'},
    sort_by='email'
)
print("Отфильтрованный и отсортированный список клиентов:", filtered_clients)

# Пример 2: Получение количества клиентов с фильтрацией
count_filtered_clients = client_db.get_count(filters={'name': 'Alice'})
print("Количество клиентов с именем 'Alice':", count_filtered_clients)

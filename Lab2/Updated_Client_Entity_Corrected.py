from abc import ABC, abstractmethod
import mysql.connector
from functools import wraps

class ClientRepositoryInterface(ABC):
    @abstractmethod
    def get_k_n_short_list(self, k, n, **kwargs):
        pass

    @abstractmethod
    def get_count(self, **kwargs):
        pass

    @abstractmethod
    def add_client(self, client_data):
        pass

    @abstractmethod
    def update_client_by_id(self, client_id, client_data):
        pass

    @abstractmethod
    def delete_client_by_id(self, client_id):
        pass

class DatabaseConnectionSingleton:
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
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


def with_filter_and_sort(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        filters = kwargs.get('filters', {})
        sort_by = kwargs.get('sort_by')
        
        filter_conditions = []
        filter_values = []
        for field, value in filters.items():
            filter_conditions.append(f"{field} = %s")
            filter_values.append(value)
        where_clause = f"WHERE {' AND '.join(filter_conditions)}" if filter_conditions else ""
        
        order_clause = f"ORDER BY {sort_by}" if sort_by else ""
        
        return func(self, *args, where_clause=where_clause, filter_values=filter_values, order_clause=order_clause)
    
    return wrapper

class ClientEntityRepDB:
    def __init__(self, db_config):
        self.db = DatabaseConnectionSingleton(db_config)

    @with_filter_and_sort
    def get_k_n_short_list(self, k, n, where_clause="", filter_values=None, order_clause=""):
        filter_values = filter_values or []
        offset = (k - 1) * n
        query = f"SELECT * FROM client {where_clause} {order_clause} LIMIT %s OFFSET %s"
        return self.db.execute_query(query, filter_values + [n, offset])

    @with_filter_and_sort
    def get_count(self, where_clause="", filter_values=None, order_clause=""):
        filter_values = filter_values or []
        query = f"SELECT COUNT(*) AS count FROM client {where_clause}"
        result = self.db.execute_query(query, filter_values)
        return result[0]['count'] if result else 0

    def add_client(self, client_data):
        query = "INSERT INTO client (name, email, phone) VALUES (%s, %s, %s)"
        params = (client_data['name'], client_data['email'], client_data['phone'])
        return self.db.execute_update(query, params)

    def update_client_by_id(self, client_id, client_data):
        query = "UPDATE client SET name = %s, email = %s, phone = %s WHERE id = %s"
        params = (client_data['name'], client_data['email'], client_data['phone'], client_id)
        self.db.execute_update(query, params)

    def delete_client_by_id(self, client_id):
        query = "DELETE FROM client WHERE id = %s"
        self.db.execute_update(query, (client_id,))

class ClientEntityRepAdapter(ClientRepositoryInterface):
    def __init__(self, db_config):
        self.client_db = ClientEntityRepDB(db_config)

    def get_k_n_short_list(self, k, n, **kwargs):
        return self.client_db.get_k_n_short_list(k, n, **kwargs)

    def get_count(self, **kwargs):
        return self.client_db.get_count(**kwargs)

    def add_client(self, client_data):
        return self.client_db.add_client(client_data)

    def update_client_by_id(self, client_id, client_data):
        self.client_db.update_client_by_id(client_id, client_data)

    def delete_client_by_id(self, client_id):
        self.client_db.delete_client_by_id(client_id)

db_config = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password',
    'database': 'database_name'
}

client_repository = ClientEntityRepAdapter(db_config)

clients = client_repository.get_k_n_short_list(1, 10, filters={'name': 'Alice'}, sort_by='email')
print("Клиенты:", clients)

count = client_repository.get_count(filters={'name': 'Alice'})
print("Количество клиентов:", count)

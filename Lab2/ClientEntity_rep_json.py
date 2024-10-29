import json
from typing import List, Dict, Any

class ClientEntity_rep_json:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        """Читает данные из JSON файла."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    def _save_data(self):
        """Сохраняет данные в JSON файл."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def get_all(self) -> List[Dict[str, Any]]:
        """Возвращает все значения."""
        return self.data

    def add_client(self, client_data: Dict[str, Any]) -> int:
        """Добавляет клиента в список и присваивает новый ID."""
        new_id = max([client["id"] for client in self.data], default=0) + 1
        client_data["id"] = new_id
        self.data.append(client_data)
        self._save_data()
        return new_id

    def get_client_by_id(self, client_id: int) -> Dict[str, Any]:
        """Возвращает объект клиента по ID."""
        for client in self.data:
            if client["id"] == client_id:
                return client
        return None

    def update_client_by_id(self, client_id: int, updated_data: Dict[str, Any]) -> bool:
        """Обновляет данные клиента по ID."""
        for idx, client in enumerate(self.data):
            if client["id"] == client_id:
                self.data[idx].update(updated_data)
                self._save_data()
                return True
        return False

    def delete_client_by_id(self, client_id: int) -> bool:
        """Удаляет клиента по ID."""
        for idx, client in enumerate(self.data):
            if client["id"] == client_id:
                del self.data[idx]
                self._save_data()
                return True
        return False

    def get_count(self) -> int:
        """Возвращает количество клиентов."""
        return len(self.data)

    def get_k_n_short_list(self, k: int, n: int) -> List[Dict[str, Any]]:
        """Возвращает список k по счету n объектов (например, вторые 20 элементов)."""
        start = (k - 1) * n
        end = start + n
        return self.data[start:end]

    def sort_by_field(self, field_name: str):
        """Сортирует клиентов по заданному полю."""
        self.data.sort(key=lambda x: x.get(field_name, ''))
        self._save_data()

    def save_all(self, new_data: List[Dict[str, Any]]):
        """Записывает все значения в файл, заменяя старые данные."""
        self.data = new_data
        self._save_data()
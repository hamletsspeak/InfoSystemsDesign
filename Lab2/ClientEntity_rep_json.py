import json
import os

class MyEntity:
    """
    Базовый класс MyEntity, представляющий сущность с id и name.
    """
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_dict(self):
        """Преобразование объекта в словарь."""
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        """Создание объекта MyEntity из словаря."""
        return cls(id=data['id'], name=data['name'])


class MyEntityRepJson:
    """
    Класс MyEntityRepJson для работы с JSON-файлом.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def read_all(self):
        """Чтение всех данных из JSON файла."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            # Преобразуем каждый элемент в экземпляр MyEntity
            return [MyEntity.from_dict(item) for item in data]
        return []

    def write_all(self, entities):
        """Запись всех данных в JSON файл."""
        with open(self.file_path, 'w') as file:
            json.dump([entity.to_dict() for entity in entities], file)

    def get_by_id(self, entity_id):
        """Получение объекта по ID."""
        entities = self.read_all()
        for entity in entities:
            if entity.id == entity_id:
                return entity
        return None

    def get_k_n_short_list(self, k, n):
        """Получение списка k по счету n объектов."""
        entities = self.read_all()
        start = (k - 1) * n
        end = start + n
        return entities[start:end]

    def sort_by_field(self, field_name):
        """Сортировка элементов по выбранному полю."""
        entities = self.read_all()
        # Сортировка по переданному полю
        sorted_entities = sorted(entities, key=lambda x: getattr(x, field_name))
        self.write_all(sorted_entities)

    def add_entity(self, new_entity):
        """Добавление нового объекта с уникальным ID."""
        entities = self.read_all()
        # Генерация нового уникального ID
        new_id = max(entity.id for entity in entities) + 1 if entities else 1
        new_entity.id = new_id
        entities.append(new_entity)
        self.write_all(entities)

    def update_entity(self, entity_id, updated_entity):
        """Обновление объекта по ID."""
        entities = self.read_all()
        for i, entity in enumerate(entities):
            if entity.id == entity_id:
                # Замена существующего объекта
                entities[i] = updated_entity
                break
        self.write_all(entities)

    def delete_entity(self, entity_id):
        """Удаление объекта по ID."""
        entities = self.read_all()
        # Исключаем объект с заданным ID
        entities = [entity for entity in entities if entity.id != entity_id]
        self.write_all(entities)

    def get_count(self):
        """Получение количества объектов."""
        return len(self.read_all())

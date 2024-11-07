import json
import yaml
import os

class MyEntity:
    """
    Базовый класс MyEntity, представляющий сущность с id и nam
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


class MyEntityRepBase:
    """
    Базовый класс для репозиториев, определяет основные методы работы с файлами.
    Подклассы MyEntityRepJson и MyEntityRepYaml будут реализовывать свои
    версии методов read_all и write_all.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def read_all(self):
        """Чтение всех данных из файла. Реализуется в дочернем классе."""
        raise NotImplementedError("Метод должен быть реализован в подклассе.")

    def write_all(self, entities):
        """Запись всех данных в файл. Реализуется в дочернем классе."""
        raise NotImplementedError("Метод должен быть реализован в подклассе.")

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
        sorted_entities = sorted(entities, key=lambda x: getattr(x, field_name))
        self.write_all(sorted_entities)

    def add_entity(self, new_entity):
        """Добавление нового объекта с уникальным ID."""
        entities = self.read_all()
        new_id = max(entity.id for entity in entities) + 1 if entities else 1
        new_entity.id = new_id
        entities.append(new_entity)
        self.write_all(entities)

    def update_entity(self, entity_id, updated_entity):
        """Обновление объекта по ID."""
        entities = self.read_all()
        for i, entity in enumerate(entities):
            if entity.id == entity_id:
                entities[i] = updated_entity
                break
        self.write_all(entities)

    def delete_entity(self, entity_id):
        """Удаление объекта по ID."""
        entities = self.read_all()
        entities = [entity for entity in entities if entity.id != entity_id]
        self.write_all(entities)

    def get_count(self):
        """Получение количества объектов."""
        return len(self.read_all())


class MyEntityRepJson(MyEntityRepBase):
    """Класс MyEntityRepJson для работы с JSON-файлом."""
    def read_all(self):
        """Чтение всех данных из JSON файла."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return [MyEntity.from_dict(item) for item in data]
        return []

    def write_all(self, entities):
        """Запись всех данных в JSON файл."""
        with open(self.file_path, 'w') as file:
            json.dump([entity.to_dict() for entity in entities], file)


class MyEntityRepYaml(MyEntityRepBase):
    """Класс MyEntityRepYaml для работы с YAML-файлом."""
    def read_all(self):
        """Чтение всех данных из YAML файла."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = yaml.safe_load(file) or []
            return [MyEntity.from_dict(item) for item in data]
        return []

    def write_all(self, entities):
        """Запись всех данных в YAML файл."""
        with open(self.file_path, 'w') as file:
            yaml.dump([entity.to_dict() for entity in entities], file)

import json
import yaml
import os

class MyEntity:
    """
    Базовый класс MyEntity, представляющий сущность с уникальными атрибутами id и name.
    """
    def __init__(self, id, name):
        # Инициализация идентификатора и имени сущности
        self.id = id
        self.name = name

    def to_dict(self):
        """Преобразование объекта MyEntity в словарь для хранения."""
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        """Создание объекта MyEntity из словаря (используется при чтении данных из файла)."""
        return cls(id=data['id'], name=data['name'])


class MyEntityRepJson:
    """
    Класс для работы с JSON-файлом, хранящим данные объектов MyEntity.
    """
    def __init__(self, file_path):
        # Путь к JSON-файлу для хранения данных
        self.file_path = file_path

    def read_all(self):
        """Чтение всех данных из JSON-файла и преобразование их в объекты MyEntity."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)  # Загрузка данных из JSON
            return [MyEntity.from_dict(item) for item in data]  # Создание объектов MyEntity
        return []

    def write_all(self, entities):
        """Запись всех объектов MyEntity в JSON-файл."""
        with open(self.file_path, 'w') as file:
            # Преобразуем объекты MyEntity в словари и записываем их в файл
            json.dump([entity.to_dict() for entity in entities], file)

    def get_by_id(self, entity_id):
        """Получение объекта MyEntity по уникальному ID."""
        entities = self.read_all()
        for entity in entities:
            if entity.id == entity_id:
                return entity  # Возвращаем объект, если ID совпадает
        return None  # Возвращаем None, если объект не найден

    def get_k_n_short_list(self, k, n):
        """
        Получение подсписка из k по счету n объектов MyEntity.
        Полезно для постраничного вывода длинного списка данных.
        """
        entities = self.read_all()
        start = (k - 1) * n  # Начало подсписка
        end = start + n  # Конец подсписка
        return entities[start:end]  # Возвращаем срез списка

    def sort_by_field(self, field_name):
        """Сортировка объектов по указанному полю и запись в файл."""
        entities = self.read_all()
        # Сортируем объекты на основе выбранного поля
        sorted_entities = sorted(entities, key=lambda x: getattr(x, field_name))
        self.write_all(sorted_entities)  # Записываем отсортированный список обратно в файл

    def add_entity(self, new_entity):
        """
        Добавление нового объекта MyEntity в файл.
        Генерация нового ID происходит автоматически.
        """
        entities = self.read_all()
        # Новый ID — на единицу больше максимального, либо 1, если список пуст
        new_id = max(entity.id for entity in entities) + 1 if entities else 1
        new_entity.id = new_id  # Присваиваем новый ID добавляемому объекту
        entities.append(new_entity)  # Добавляем объект в список
        self.write_all(entities)  # Записываем обновленный список в файл

    def update_entity(self, entity_id, updated_entity):
        """
        Обновление объекта MyEntity в файле по ID.
        Если объект с таким ID найден, он заменяется новым значением.
        """
        entities = self.read_all()
        for i, entity in enumerate(entities):
            if entity.id == entity_id:
                entities[i] = updated_entity  # Обновляем объект
                break
        self.write_all(entities)  # Записываем изменения в файл

    def delete_entity(self, entity_id):
        """Удаление объекта MyEntity по ID из файла."""
        entities = self.read_all()
        # Формируем новый список без объекта с заданным ID
        entities = [entity for entity in entities if entity.id != entity_id]
        self.write_all(entities)  # Записываем обновленный список

    def get_count(self):
        """Возвращает количество объектов MyEntity в файле."""
        return len(self.read_all())  # Количество объектов в файле


class MyEntityRepYaml(MyEntityRepJson):
    """
    Класс MyEntityRepYaml для работы с YAML-файлом, наследующий методы базового класса JSON-репозитория.
    Переопределяет методы для работы с YAML.
    """
    def read_all(self):
        """Чтение всех данных из YAML-файла и преобразование их в объекты MyEntity."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = yaml.safe_load(file)  # Загрузка данных из YAML
            return [MyEntity.from_dict(item) for item in data]  # Создание объектов MyEntity
        return []

    def write_all(self, entities):
        """Запись всех объектов MyEntity в YAML-файл."""
        with open(self.file_path, 'w') as file:
            # Преобразуем объекты MyEntity в словари и записываем их в файл
            yaml.dump([entity.to_dict() for entity in entities], file)

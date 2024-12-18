import json
import os

class MyEntity:
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'], name=data['name'])

class MyEntityRepJson:

    def __init__(self, file_path):
        self.file_path = file_path

    def read_all(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return [MyEntity.from_dict(item) for item in data]
        return []

    def write_all(self, entities):
        with open(self.file_path, 'w') as file:
            json.dump([entity.to_dict() for entity in entities], file)

    def get_by_id(self, entity_id):
        entities = self.read_all()
        for entity in entities:
            if entity.id == entity_id:
                return entity
        return None

    def get_k_n_short_list(self, k, n):
        entities = self.read_all()
        start = (k - 1) * n
        end = start + n
        return entities[start:end]

    def sort_by_field(self, field_name):
        entities = self.read_all()
        sorted_entities = sorted(entities, key=lambda x: getattr(x, field_name))
        self.write_all(sorted_entities)

    def add_entity(self, new_entity):
        entities = self.read_all()
        new_id = max(entity.id for entity in entities) + 1 if entities else 1
        new_entity.id = new_id
        entities.append(new_entity)
        self.write_all(entities)

    def update_entity(self, entity_id, updated_entity):
        entities = self.read_all()
        for i, entity in enumerate(entities):
            if entity.id == entity_id:
                entities[i] = updated_entity
                break
        self.write_all(entities)

    def delete_entity(self, entity_id):
        entities = self.read_all()
        entities = [entity for entity in entities if entity.id != entity_id]
        self.write_all(entities)

    def get_count(self):
        return len(self.read_all())

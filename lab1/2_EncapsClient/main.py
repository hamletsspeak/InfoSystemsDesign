import json
    
class ClientBase:
    @staticmethod
    def validate_field(field, field_name, min_length):
        if not field or len(field) < min_length:
            raise ValueError(f"{field_name} должно содержать не менее {min_length} символов.")
        return True

    def __init__(self, last_name, first_name, middle_name, passport_data, phone):
        self.__last_name = last_name
        self.__first_name = first_name
        self.__middle_name = middle_name
        self.__passport_data = passport_data
        self.__phone = phone

        # Валидация данных
        self.validate_field(last_name, "Фамилия", 2)
        self.validate_field(first_name, "Имя", 2)
        self.validate_field(middle_name, "Отчество", 2)
        self.validate_passport_data(passport_data)
        self.validate_phone(phone)
        
    @staticmethod
    def from_string(data_string):
        fields = data_string.split(',')
        if len(fields) != 5:
            raise ValueError("Неверный формат строки для создания объекта.")
        return ClientBase(*fields)

    @staticmethod
    def from_json(json_string):
        data = json.loads(json_string)
        return ClientBase(**data)


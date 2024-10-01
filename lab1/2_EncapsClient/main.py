class ClientBase:
    def __init__(self, last_name, first_name, middle_name, passport_data, phone):
        self.__last_name = last_name
        self.__first_name = first_name
        self.__middle_name = middle_name
        self.__passport_data = passport_data
        self.__phone = phone

    # Методы для получения данных
    def get_last_name(self):
        return self.__last_name

    def get_first_name(self):
        return self.__first_name

    def get_middle_name(self):
        return self.__middle_name

    def get_passport_data(self):
        return self.__passport_data

    def get_phone(self):
        return self.__phone
import json

# Класс для залогового объекта
class PledgeItem:
    def __init__(self, item_name, item_value, loan_amount, return_date):
        self.__item_name = self.validate_field(item_name, "Item name", max_length=100)
        self.__item_value = self.validate_number(item_value, "Item value")
        self.__loan_amount = self.validate_number(loan_amount, "Loan amount")
        self.__return_date = return_date  # Дата возврата залога (должна быть объектом типа дата)

    # Валидация числовых значений
    @staticmethod
    def validate_number(value, field_name):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{field_name} must be a positive number")
        return value

    # Универсальная валидация строк
    @staticmethod
    def validate_field(value, field_name, max_length=None):
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        if max_length and len(value) > max_length:
            raise ValueError(f"{field_name} must not exceed {max_length} characters")
        return value

    def __str__(self):
        return (f"Item: {self.__item_name}, Value: {self.__item_value}, "
                f"Loan: {self.__loan_amount}, Return Date: {self.__return_date}")


# Базовый класс клиента
class ClientBase:
    def __init__(self, last_name=None, first_name=None, middle_name=None, address=None, phone=None, data=None):
        if data:
            # Инициализация через строку, JSON или словарь
            if isinstance(data, str):
                try:
                    parsed_data = json.loads(data)
                    self.__init_from_dict(parsed_data)
                except json.JSONDecodeError:
                    self.__init_from_string(data)
            elif isinstance(data, dict):
                self.__init_from_dict(data)
            else:
                raise ValueError("Invalid data format. Expected JSON string, plain string, or dictionary.")
        else:
            # Стандартная инициализация через параметры
            self.__last_name = self.validate_field(last_name, "Last name", is_alpha=True, max_length=50)
            self.__first_name = self.validate_field(first_name, "First name", is_alpha=True, max_length=50)
            self.__middle_name = self.validate_field(middle_name, "Middle name", is_alpha=True, max_length=50)
            self.__address = self.validate_field(address, "Address", max_length=100)
            self.__phone = self.validate_field(phone, "Phone number", is_phone=True, exact_length=12)

    # Вспомогательные методы инициализации
    def __init_from_string(self, data_str):
        parts = data_str.split()
        if len(parts) != 5:
            raise ValueError("Invalid string format. Expected: 'LastName FirstName MiddleName Address Phone'")
        
        self.__last_name = self.validate_field(parts[0], "Last name", is_alpha=True, max_length=50)
        self.__first_name = self.validate_field(parts[1], "First name", is_alpha=True, max_length=50)
        self.__middle_name = self.validate_field(parts[2], "Middle name", is_alpha=True, max_length=50)
        self.__address = self.validate_field(parts[3], "Address", max_length=100)
        self.__phone = self.validate_field(parts[4], "Phone number", is_phone=True, exact_length=12)

    def __init_from_dict(self, data_dict):
        try:
            self.__last_name = self.validate_field(data_dict['last_name'], "Last name", is_alpha=True, max_length=50)
            self.__first_name = self.validate_field(data_dict['first_name'], "First name", is_alpha=True, max_length=50)
            self.__middle_name = self.validate_field(data_dict['middle_name'], "Middle name", is_alpha=True, max_length=50)
            self.__address = self.validate_field(data_dict['address'], "Address", max_length=100)
            self.__phone = self.validate_field(data_dict['phone'], "Phone number", is_phone=True, exact_length=12)
        except KeyError as e:
            raise ValueError(f"Missing key in JSON or dict: {e}")

    # Валидация полей
    @staticmethod
    def validate_field(value, field_name, is_alpha=False, is_phone=False, max_length=None, exact_length=None):
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        if max_length and len(value) > max_length:
            raise ValueError(f"{field_name} must not exceed {max_length} characters")
        if exact_length and len(value) != exact_length:
            raise ValueError(f"{field_name} must be exactly {exact_length} characters")
        if is_alpha and not value.isalpha():
            raise ValueError(f"{field_name} must contain only alphabetic characters")
        if is_phone and (not value.startswith('+') or not value[1:].isdigit()):
            raise ValueError(f"{field_name} must be in the format '+1234567890'")
        return value

    # Геттеры
    def get_last_name(self):
        return self.__last_name

    def get_first_name(self):
        return self.__first_name

    def get_middle_name(self):
        return self.__middle_name

    def get_address(self):
        return self.__address

    def get_phone(self):
        return self.__phone




    # Полная версия объекта (с выводом всех полей)
    def __eq__(self, other):
        if isinstance(other, ClientBase):
            return (self.__last_name == other.__last_name and
                    self.__first_name == other.__first_name and
                    self.__middle_name == other.__middle_name and
                    self.__passport_data == other.__passport_data and
                    self.__phone == other.__phone)
        return False

class Client(ClientBase):
    def __str__(self):
        return (f"Client: {self.get_last_name()} {self.get_first_name()} {self.get_middle_name()}\n"
                f"Passport Data: {self.get_passport_data()}\n"
                f"Phone: {self.get_phone()}")

class ClientShortInfo(ClientBase):
    def __str__(self):
        return f"Client: {self.get_last_name()} {self.get_first_name()[0]}. {self.get_middle_name()[0]}. - Phone: {self.get_phone()}"

    # Сравнение объектов на равенство
    def __eq__(self, other):
        if isinstance(other, ClientBase):
            return (self.__last_name == other.__last_name and
                    self.__first_name == other.__first_name and
                    self.__middle_name == other.__middle_name and
                    self.__address == other.__address and
                    self.__phone == other.__phone)
        return False


# Класс Client с залогами
class Client(ClientBase):
    def __init__(self, last_name=None, first_name=None, middle_name=None, address=None, phone=None, pledges=None, data=None):
        super().__init__(last_name, first_name, middle_name, address, phone, data)
        self.__pledges = pledges or []  # Список залогов
    
    def add_pledge(self, pledge_item):
        if isinstance(pledge_item, PledgeItem):
            self.__pledges.append(pledge_item)
        else:
            raise ValueError("Invalid pledge item")

    def __str__(self):
        pledges_info = "\n".join([str(pledge) for pledge in self.__pledges]) if self.__pledges else "No pledges"
        return (f"Client: {self.get_last_name()} {self.get_first_name()} {self.get_middle_name()}\n"
                f"Address: {self.get_address()}\n"
                f"Phone: {self.get_phone()}\n"
                f"Pledges:\n{pledges_info}")


# Краткая информация о клиенте
class ClientShortInfo(ClientBase):
    def __str__(self):
        return f"Client: {self.get_last_name()} {self.get_first_name()} - Phone: {self.get_phone()}"


# Пример использования
try:
    # Создаем объект Client (полная версия)
    client1 = Client("Ivanov", "Ivan", "Ivanovich", "123 Main St", "+1234567890")
    
    # Добавляем залоговый объект
    pledge1 = PledgeItem("Watch", 10000, 5000, "2024-12-01")
    client1.add_pledge(pledge1)
    
    # Создаем объект ClientShortInfo (краткая версия)
    client_short_info = ClientShortInfo("Ivanov", "Ivan", "Ivanovich", "123 Main St", "+1234567890")
    
    # Вывод полной версии клиента
    print("Полная версия клиента:")
    print(client1)  # Output: Полная информация о клиенте
    
    # Вывод краткой версии клиента
    print("\nКраткая версия клиента:")
    print(client_short_info)  # Output: Краткая информация о клиенте

except ValueError as e:
    print(e)
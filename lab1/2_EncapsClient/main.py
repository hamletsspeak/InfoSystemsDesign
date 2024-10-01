class ClientBase:
    @staticmethod
    def validate_name(name):
        if not name or len(name) < 2:
            raise ValueError("Имя должно содержать не менее 2 символов.")
        return True

    @staticmethod
    def validate_passport_data(passport_data):
        if len(passport_data) != 10:
            raise ValueError("Паспортные данные должны содержать 10 символов.")
        return True

    @staticmethod
    def validate_phone(phone):
        if not phone.startswith('+') or len(phone) < 10:
            raise ValueError("Номер телефона должен начинаться с '+' и содержать не менее 10 цифр.")
        return True

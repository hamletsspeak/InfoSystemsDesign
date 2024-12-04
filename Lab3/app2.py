import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re

# ---------- МОДЕЛЬ ---------- #
class ClientRepositorySQLite:
    """Репозиторий клиентов для работы с SQLite."""
    def __init__(self, db_name="pawnshop.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()  # Обновим таблицу при инициализации
        self.observers = []  # Список наблюдателей

    def add_observer(self, observer):
        """Добавить наблюдателя."""
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        """Удалить наблюдателя."""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self):
        """Уведомить всех наблюдателей об изменениях."""
        for observer in self.observers:
            observer.update()

    def add_client(self, client_data):
        """Добавление нового клиента."""
        self.cursor.execute("""
            INSERT INTO clients (fio, phone, address, inn, birth_date, item, value, term)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_data['fio'], client_data['phone'],
              client_data['address'], client_data['inn'], client_data['birth_date'],
              client_data['item'], client_data['value'], client_data['term']))
        self.conn.commit()
        self.notify_observers()  # Уведомляем наблюдателей

    def delete_client(self, client_id):
        """Удаление клиента по ID."""
        self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        self.conn.commit()
        self.notify_observers()  # Уведомляем наблюдателей

    def update_client(self, client_id, client_data):
        """Обновление данных клиента."""
        self.cursor.execute("""
            UPDATE clients
            SET fio = ?, phone = ?, address = ?, inn = ?, birth_date = ?
            WHERE id = ?
        """, (client_data['fio'], client_data['phone'],
              client_data['address'], client_data['inn'], client_data['birth_date'], client_id))
        self.conn.commit()
        self.notify_observers()  # Уведомляем наблюдателей

    def _create_table(self):
        """Создание или обновление таблицы клиентов."""
        # Создание таблицы с основными колонками
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        self.conn.commit()

        # Проверяем наличие дополнительных колонок и добавляем их при необходимости
        existing_columns = self._get_existing_columns()

        # Добавляем новые колонки, если их нет
        if "address" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN address TEXT")
        if "inn" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN inn TEXT")
        if "birth_date" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN birth_date TEXT")
        if "item" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN item TEXT")
        if "value" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN value REAL")
        if "term" not in existing_columns:
            self.cursor.execute("ALTER TABLE clients ADD COLUMN term INTEGER")

        self.conn.commit()

    def _get_existing_columns(self):
        """Получение списка существующих колонок в таблице."""
        self.cursor.execute("PRAGMA table_info(clients)")
        return [row[1] for row in self.cursor.fetchall()]


    def get_client_by_id(self, client_id):
        """Получение полной информации о клиенте по ID."""
        self.cursor.execute("SELECT fio, phone, address, inn, birth_date, item, value, term FROM clients WHERE id = ?", (client_id,))
        return self.cursor.fetchone()


    def get_all_clients(self):
        """Получение всех клиентов."""
        self.cursor.execute("SELECT id, fio, phone FROM clients")
        return self.cursor.fetchall()


# ---------- КОНТРОЛЛЕР ---------- #
class MainController:
    """Контроллер для главного окна."""
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.update_view()

    def update_view(self):
        """Обновление данных в таблице."""
        clients = self.model.get_all_clients()
        self.view.update_table(clients)

    def add_client(self, client_data):
        """Добавление клиента через модель."""
        self.model.add_client(client_data)
        self.update_view()

    def delete_client(self, client_id):
        """Удаление клиента через модель."""
        if client_id:
            self.model.delete_client(client_id)
            self.update_view()

    def on_add_button_click(self):
        """Открытие окна добавления клиента."""
        AddClientController(self.model, self)

    def show_client_info(self, client_id):
        """Открытие окна с полной информацией о клиенте."""
        if client_id:
            ClientInfoView(self.model, client_id)
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные клиента!")

    def edit_client(self, client_id):
        """Открытие окна редактирования клиента."""
        if client_id:
            EditClientController(self.model, self, client_id)
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования!")

class AddClientController:
    """Контроллер для окна добавления клиента."""
    def __init__(self, model, main_controller):
        self.model = model
        self.main_controller = main_controller
        self.view = AddClientView(self)

    def submit_client(self, client_data):
        """Сохранение нового клиента с валидацией."""
        # Проверка ФИО
        if not client_data['fio'] or not client_data['fio'].replace(" ", "").isalpha():
            messagebox.showerror("Ошибка", "ФИО должно содержать только буквы и не быть пустым!")
            return

        # Проверка телефона
        phone_pattern = r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$"
        if not re.match(phone_pattern, client_data['phone']):
            messagebox.showerror("Ошибка", "Телефон должен быть в формате +7 (xxx) xxx-xx-xx!")
            return

        # Проверка даты рождения
        birth_date_pattern = r"^\d{2}-\d{2}-\d{4}$"
        if not re.match(birth_date_pattern, client_data['birth_date']):
            messagebox.showerror("Ошибка", "Дата рождения должна быть в формате ДД-ММ-ГГГГ!")
            return
        
        # Если проверка прошла, добавляем клиента
        self.model.add_client(client_data)
        self.main_controller.update_view()
        self.view.close_window()

class EditClientController:
    """Контроллер для окна редактирования клиента."""
    def __init__(self, model, main_controller, client_id):
        self.model = model
        self.main_controller = main_controller
        self.client_id = client_id
        client_data = self.model.get_client_by_id(client_id)
        if client_data:
            client_data = dict(zip(["fio", "phone", "address", "inn", "birth_date"], client_data))
            self.view = EditClientView(self, client_data)

    def save_client(self, client_data):
        """Сохранение изменений клиента."""
        self.model.update_client(self.client_id, client_data)
        self.main_controller.update_view()
        self.view.close_window()


# ---------- ПРЕДСТАВЛЕНИЕ ---------- #
class MainView(tk.Tk):
    """Главное окно приложения."""
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.title("Ломбард - Главное окно")
        self.geometry("1200x400")

        # Таблица
        self.tree = ttk.Treeview(self, columns=("ID", "FIO", "Phone"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("FIO", text="ФИО")
        self.tree.heading("Phone", text="Телефон")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки
        add_button = ttk.Button(self, text="Добавить клиента", command=self.on_add_button_click)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

        delete_button = ttk.Button(self, text="Удалить клиента", command=self.on_delete_button_click)
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)

        info_button = ttk.Button(self, text="Посмотреть информацию", command=self.on_info_button_click)
        info_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_button = ttk.Button(self, text="Редактировать клиента", command=self.on_edit_button_click)
        edit_button.pack(side=tk.LEFT, padx=10, pady=10)

    def on_edit_button_click(self):
        """Обработчик для кнопки редактирования клиента."""
        selected_item = self.tree.selection()
        if selected_item:
            client_id = self.tree.item(selected_item[0], "values")[0]  # Получаем ID клиента
            if self.controller:
                self.controller.edit_client(client_id)
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования!")

    def on_info_button_click(self):
        """Обработчик для кнопки 'Посмотреть информацию'."""
        selected_item = self.tree.selection()
        if selected_item:
            client_id = self.tree.item(selected_item[0], "values")[0]  # Получаем ID клиента
            if self.controller:
                self.controller.show_client_info(client_id)
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для просмотра информации!")

    def sort_table(self, column):
        """Сортировка таблицы по указанному столбцу."""
        # Индекс столбца для сортировки
        column_index = {"ID": 0, "FIO": 1, "Phone": 2}[column]

        # Получаем текущие данные из таблицы
        data = [(self.tree.item(item)["values"], item) for item in self.tree.get_children()]

        # Определяем порядок сортировки
        reverse = self.sort_order[column]
        data.sort(key=lambda x: x[0][column_index], reverse=reverse)

        # Переключаем порядок сортировки
        self.sort_order[column] = not reverse

        # Удаляем старые строки и вставляем их в новом порядке
        self.tree.delete(*self.tree.get_children())
        for values, _ in data:
            self.tree.insert("", tk.END, values=values)

    def update_table(self, clients):
        """Обновление данных таблицы."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for client in clients:
            self.tree.insert("", tk.END, values=client)

    def on_add_button_click(self):
        """Обработчик для кнопки добавления клиента."""
        if self.controller:
            self.controller.on_add_button_click()
        else:
            messagebox.showerror("Ошибка", "Контроллер не привязан!")

    def on_delete_button_click(self):
        """Обработчик для кнопки удаления клиента."""
        selected_item = self.tree.selection()
        if selected_item:
            client_id = self.tree.item(selected_item[0], "values")[0]  # Получаем ID
            client_name = self.tree.item(selected_item[0], "values")[1]  # Получаем ФИО для подтверждения

            # Окно подтверждения
            confirm = messagebox.askyesno(
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить клиента: {client_name}?"
            )

            if confirm:  # Если пользователь нажал "Да"
                if self.controller:
                    self.controller.delete_client(client_id)
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для удаления!")

class AddClientView(tk.Toplevel):
    """Окно для добавления нового клиента."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Добавить клиента")
        self.geometry("300x500")

        # Метки и поля ввода
        tk.Label(self, text="ФИО (например, Иван Иванов):").pack(pady=5, anchor=tk.W, padx=10)
        self.fio_entry = ttk.Entry(self)
        self.fio_entry.pack(pady=5, padx=10, fill=tk.X)

        tk.Label(self, text="Телефон (формат: +7 (___) ___-__-__):").pack(pady=5, anchor=tk.W, padx=10)

        # Поле ввода телефона
        self.phone_var = tk.StringVar(value="+7 (   )    -  -  ")  # Предустановленный шаблон
        self.phone_entry = ttk.Entry(self, textvariable=self.phone_var)
        self.phone_entry.pack(pady=5, padx=10, fill=tk.X)

        # Ограничение ввода через обработчик событий
        self.phone_entry.bind("<KeyRelease>", self.format_phone)

        # Поле для ввода адреса
        tk.Label(self, text="Адрес:").pack(pady=5, anchor=tk.W, padx=10)
        self.address_entry = ttk.Entry(self)
        self.address_entry.pack(pady=5, padx=10, fill=tk.X)

        # Поле для ввода ИНН
        tk.Label(self, text="ИНН:").pack(pady=5, anchor=tk.W, padx=10)
        self.inn_entry = ttk.Entry(self)
        self.inn_entry.pack(pady=5, padx=10, fill=tk.X)

        # Поле для ввода даты рождения
        tk.Label(self, text="Дата рождения (ДД-ММ-ГГГГ):").pack(pady=5, anchor=tk.W, padx=10)
        self.birth_date_entry = ttk.Entry(self)
        self.birth_date_entry.pack(pady=5, padx=10, fill=tk.X)
        
        # Поле для ввода предмета залога
        tk.Label(self, text="Предмет залога:").pack(pady=5, anchor=tk.W, padx=10)
        self.item_entry = ttk.Entry(self)
        self.item_entry.pack(pady=5, padx=10, fill=tk.X)

        # Поле для ввода стоимости залога
        tk.Label(self, text="Стоимость залога:").pack(pady=5, anchor=tk.W, padx=10)
        self.value_entry = ttk.Entry(self)
        self.value_entry.pack(pady=5, padx=10, fill=tk.X)

        # Поле для ввода срока залога в месяцах
        tk.Label(self, text="Срок залога (в месяцах):").pack(pady=5, anchor=tk.W, padx=10)
        self.term_entry = ttk.Entry(self)
        self.term_entry.pack(pady=5, padx=10, fill=tk.X)

        # Кнопка "Сохранить"
        submit_button = ttk.Button(self, text="Сохранить", command=self.submit)
        submit_button.pack(pady=10)

    def format_phone(self, event):
        """Форматирование телефона по шаблону."""
        cursor_position = self.phone_entry.index(tk.INSERT)  # Текущая позиция курсора
        value = self.phone_var.get()
        digits = [c for c in value if c.isdigit()]  # Оставляем только цифры

        # Формируем шаблон
        formatted = "+7 ("
        if len(digits) > 1:
            formatted += "".join(digits[1:4])  # Код региона
        formatted += ") "
        if len(digits) > 4:
            formatted += "".join(digits[4:7])  # Первые 3 цифры
        formatted += "-"
        if len(digits) > 7:
            formatted += "".join(digits[7:9])  # Две цифры
        formatted += "-"
        if len(digits) > 9:
            formatted += "".join(digits[9:11])  # Последние две цифры

        # Устанавливаем значение в поле ввода
        self.phone_var.set(formatted)

        # Перемещаем курсор на правильную позицию
        if cursor_position < len(self.phone_var.get()):
            self.phone_entry.icursor(cursor_position)

    def submit(self):
        """Сохранение данных с валидацией."""
        client_data = {
            "fio": self.fio_entry.get(),
            "phone": self.phone_var.get(),
            "address": self.address_entry.get(),
            "inn": self.inn_entry.get(),
            "birth_date": self.birth_date_entry.get(),
            "item": self.item_entry.get(),
            "value": self.value_entry.get(),
            "term": self.term_entry.get()
        }
        self.controller.submit_client(client_data)

    def close_window(self):
        """Закрытие окна."""
        self.destroy()

class EditClientView(tk.Toplevel):
    """Окно для редактирования клиента."""
    def __init__(self, controller, client_data):
        super().__init__()
        self.controller = controller
        self.title("Редактировать клиента")
        self.geometry("300x500")

        # Поля ввода с предзаполненными данными
        self.fio_entry = self._create_entry("ФИО", client_data['fio'])
        self.phone_var = tk.StringVar(value=client_data['phone'] or "+7 (   )    -  -  ")
        self.phone_entry = self._create_entry_with_var("Телефон", self.phone_var)
        self.phone_entry.bind("<KeyRelease>", self.format_phone)

        self.address_entry = self._create_entry("Адрес", client_data['address'])
        self.inn_entry = self._create_entry("ИНН", client_data['inn'])
        self.birth_date_entry = self._create_entry("Дата рождения", client_data['birth_date'])

        # Кнопка сохранения
        save_button = ttk.Button(self, text="Сохранить", command=self.save_client)
        save_button.pack(pady=10)

    def _create_entry(self, label_text, initial_value):
        tk.Label(self, text=label_text).pack(pady=5, anchor=tk.W, padx=10)
        entry = ttk.Entry(self)
        entry.insert(0, initial_value)
        entry.pack(pady=5, padx=10, fill=tk.X)
        return entry

    def _create_entry_with_var(self, label_text, text_var):
        tk.Label(self, text=label_text).pack(pady=5, anchor=tk.W, padx=10)
        entry = ttk.Entry(self, textvariable=text_var)
        entry.pack(pady=5, padx=10, fill=tk.X)
        return entry

    def format_phone(self, event):
        """Форматирование телефона по шаблону."""
        cursor_position = self.phone_entry.index(tk.INSERT)  # Текущая позиция курсора
        value = self.phone_var.get()
        digits = [c for c in value if c.isdigit()]  # Оставляем только цифры

        # Формируем шаблон
        formatted = "+7 ("
        if len(digits) > 1:
            formatted += "".join(digits[1:4])  # Код региона
        formatted += ") "
        if len(digits) > 4:
            formatted += "".join(digits[4:7])  # Первые 3 цифры
        formatted += "-"
        if len(digits) > 7:
            formatted += "".join(digits[7:9])  # Две цифры
        formatted += "-"
        if len(digits) > 9:
            formatted += "".join(digits[9:11])  # Последние две цифры

        # Устанавливаем значение в поле ввода
        self.phone_var.set(formatted)

        # Перемещаем курсор на правильную позицию
        if cursor_position < len(self.phone_var.get()):
            self.phone_entry.icursor(cursor_position)

    def save_client(self):
        """Сохранение данных с валидацией."""
        client_data = {
            "fio": self.fio_entry.get(),
            "phone": self.phone_var.get(),
            "address": self.address_entry.get(),
            "inn": self.inn_entry.get(),
            "birth_date": self.birth_date_entry.get(),
        }
        self.controller.save_client(client_data)

    def close_window(self):
        """Закрытие окна."""
        self.destroy()


# ---------- ОКНО ПОЛНОЙ ИНФОРМАЦИИ О КЛИЕНТЕ ---------- #
class ClientInfoView(tk.Toplevel):
    """Окно для отображения полной информации о клиенте."""
    def __init__(self, model, client_id):
        super().__init__()
        self.model = model
        self.client_id = client_id
        self.title("Полная информация о клиенте")
        self.geometry("400x400")

        self.client_data = self.model.get_client_by_id(client_id)  # Получаем данные клиента из базы
        if not self.client_data:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные клиента!")
            self.destroy()
            return

        self.info_labels = {}
        self._create_widgets()
        self.update()  # Обновление данных в окне

    def _create_widgets(self):
        """Создание виджетов для отображения информации."""
        fields = ["ФИО", "Телефон", "Адрес", "ИНН", "Дата рождения", "Предмет залога", "Стоимость", "Срок залога"]
        for i, field in enumerate(fields):
            tk.Label(self, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            self.info_labels[field] = tk.Label(self, text="")  # Для отображения информации
            self.info_labels[field].grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)

    def update(self):
        """Обновление данных в окне."""
        if self.client_data:
            labels = ["fio", "phone", "address", "inn", "birth_date", "item", "value", "term"]
            field_names = ["ФИО", "Телефон", "Адрес", "ИНН", "Дата рождения", "Предмет залога", "Стоимость", "Срок залога"]
            
            for field, name in zip(labels, field_names):
                self.info_labels[name].config(text=self.client_data[labels.index(field)])

    def close_window(self):
        """Закрытие окна."""
        self.destroy()

    def on_add_button_click(self):
        """Обработчик для кнопки добавления клиента."""
        if self.controller:
            self.controller.on_add_button_click()
        else:
            messagebox.showerror("Ошибка", "Контроллер не привязан!")

    def edit_client(self, client_id):
        """Открытие окна редактирования клиента."""
        if client_id:
            EditClientController(self.model, self, client_id)
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования!")


# ---------- ЗАПУСК ---------- #
if __name__ == "__main__":
    client_repo = ClientRepositorySQLite()  # Репозиторий для работы с SQLite
    main_view = MainView(None)  # Создаём главное окно (временно без контроллера)
    main_controller = MainController(main_view, client_repo)  # Контроллер связывает представление и модель
    main_view.controller = main_controller  # Устанавливаем контроллер в главное окно
    main_view.mainloop()  # Запускаем главное окно

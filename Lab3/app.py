import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import sqlite3
import re


# ---------- МОДЕЛЬ ---------- #
class ClientRepositorySQLite:
    """Репозиторий клиентов для работы с SQLite."""
    def __init__(self, db_name="pawnshop.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Создание таблицы клиентов, если она ещё не существует."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                phone TEXT NOT NULL,
                pledges INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def add_client(self, client_data):
        """Добавление нового клиента."""
        self.cursor.execute("""
            INSERT INTO clients (fio, phone, pledges)
            VALUES (?, ?, ?)
        """, (client_data['fio'], client_data['phone'], client_data['pledges']))
        self.conn.commit()

    def get_all_clients(self):
        """Получение всех клиентов."""
        self.cursor.execute("SELECT id, fio, phone, pledges FROM clients")
        return self.cursor.fetchall()
    
    def delete_client(self, client_id):
        """Удаление клиента по ID."""
        self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        self.conn.commit()


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

        # Если проверка прошла, добавляем клиента
        self.model.add_client(client_data)
        self.main_controller.update_view()
        self.view.close_window()


# ---------- ПРЕДСТАВЛЕНИЕ ---------- #
class MainView(tk.Tk):
    """Главное окно приложения."""
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.title("Ломбард - Главное окно")
        self.geometry("600x400")

        # Таблица
        self.tree = ttk.Treeview(self, columns=("ID", "FIO", "Phone", "Pledges"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("FIO", text="ФИО")
        self.tree.heading("Phone", text="Телефон")
        self.tree.heading("Pledges", text="Количество залогов")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки
        add_button = ttk.Button(self, text="Добавить клиента", command=self.on_add_button_click)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        delete_button = ttk.Button(self, text="Удалить клиента", command=self.on_delete_button_click)
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)

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

    
    def update_table(self, clients):
        """Обновление данных таблицы."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for client in clients:
            self.tree.insert("", tk.END, values=client)


class AddClientView(tk.Toplevel):
    """Окно для добавления нового клиента."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Добавить клиента")
        self.geometry("300x200")

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
            "pledges": 0  # Новый клиент без залогов
        }
        self.controller.submit_client(client_data)

    def close_window(self):
        """Закрытие окна."""
        self.destroy()


# ---------- ЗАПУСК ---------- #
if __name__ == "__main__":
    client_repo = ClientRepositorySQLite()  # Репозиторий для работы с SQLite
    main_view = MainView(None)  # Создаём главное окно (временно без контроллера)
    main_controller = MainController(main_view, client_repo)  # Контроллер связывает представление и модель
    main_view.controller = main_controller  # Устанавливаем контроллер в главное окно
    main_view.mainloop()  # Запускаем главное окно

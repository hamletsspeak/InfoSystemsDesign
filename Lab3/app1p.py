import tkinter as tk
from tkinter import ttk
from typing import List
import sqlite3
import re

# ---------- МОДЕЛЬ ---------- #
class ClientRepositorySQLite:
    """Репозиторий клиентов для работы с SQLite."""
    def __init__(self, db_name="pawnshop.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._observers = []  # Список наблюдателей

    def subscribe(self, observer):
        """Добавление наблюдателя."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        """Удаление наблюдателя."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """Оповещение всех наблюдателей."""
        for observer in self._observers:
            observer.update()

    def update_client(self, client_id, client_data):
        """Обновление данных клиента."""
        self.cursor.execute("""
            UPDATE clients
            SET fio = ?, phone = ?, address = ?, inn = ?, birth_date = ?
            WHERE id = ?
        """, (client_data['fio'], client_data['phone'],
              client_data['address'], client_data['inn'], client_data['birth_date'], client_id))
        self.conn.commit()
        self._notify_observers()

    def add_client(self, client_data):
        """Добавление нового клиента."""
        self.cursor.execute("""
            INSERT INTO clients (fio, phone, address, inn, birth_date)
            VALUES (?, ?, ?, ?, ?)
        """, (client_data['fio'], client_data['phone'],
              client_data['address'], client_data['inn'], client_data['birth_date']))
        self.conn.commit()
        self._notify_observers()

    def delete_client(self, client_id):
        """Удаление клиента по ID."""
        self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        self.conn.commit()
        self._notify_observers()

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
        self.model.subscribe(self)  # Подписываемся на обновления модели
        self.update_view()

    def update(self):
        """Метод, вызываемый при изменении данных в модели."""
        self.update_view()

    def update_view(self):
        """Обновление данных в таблице."""
        clients = self.model.get_all_clients()
        self.view.update_table(clients)

    def add_client(self, client_data):
        """Добавление клиента через модель."""
        self.model.add_client(client_data)

    def delete_client(self, client_id):
        """Удаление клиента через модель."""
        if client_id:
            self.model.delete_client(client_id)

    def __del__(self):
        """Отписываемся от модели при удалении контроллера."""
        self.model.unsubscribe(self)


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

    def on_add_button_click(self):
        """Обработчик для кнопки добавления клиента."""
        # Заглушка для добавления
        if self.controller:
            self.controller.add_client({
                "fio": "Иван Иванов",
                "phone": "+7 (900) 123-45-67",
                "address": "Москва",
                "inn": "1234567890",
                "birth_date": "01-01-1990"
            })

    def on_delete_button_click(self):
        """Обработчик для кнопки удаления клиента."""
        selected_item = self.tree.selection()
        if selected_item:
            client_id = self.tree.item(selected_item[0], "values")[0]  # Получаем ID
            if self.controller:
                self.controller.delete_client(client_id)

    def update_table(self, clients):
        """Обновление данных таблицы."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for client in clients:
            self.tree.insert("", tk.END, values=client)


# ---------- ЗАПУСК ---------- #
if __name__ == "__main__":
    client_repo = ClientRepositorySQLite()  # Репозиторий для работы с SQLite
    main_view = MainView(None)  # Создаём главное окно (временно без контроллера)
    main_controller = MainController(main_view, client_repo)  # Контроллер связывает представление и модель
    main_view.controller = main_controller  # Устанавливаем контроллер в главное окно
    main_view.mainloop()  # Запускаем главное окно
# Новый файл с реализацией задания с паттерном "Наблюдатель"

import tkinter as tk
from tkinter import ttk
from typing import List


# ---------- МОДЕЛЬ (с использованием паттерна "Наблюдатель") ---------- #
class Observer:
    """Интерфейс для реализации паттерна 'Наблюдатель'."""
    def update(self):
        raise NotImplementedError("Метод update() должен быть переопределён")


class Observable:
    """Класс, реализующий функциональность наблюдаемого объекта."""
    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update()


class ClientRepository(Observable):
    """Репозиторий клиентов для работы с хранилищем."""
    def __init__(self):
        super().__init__()
        self.clients = [
            {"fio": "Иванов Иван Иванович", "phone": "+7 (123) 456-78-90", "pledges": 2},
            {"fio": "Петров Петр Петрович", "phone": "+7 (234) 567-89-01", "pledges": 1},
        ]

    def get_all_clients(self):
        """Получение всех клиентов."""
        return self.clients

    def add_client(self, client_data):
        """Добавление клиента."""
        self.clients.append(client_data)
        self.notify_observers()


# ---------- КОНТРОЛЛЕР ---------- #
class MainController:
    """Контроллер для главного окна."""
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.model.add_observer(self)  # Подписываем контроллер на обновления модели
        self.update()

    def update(self):
        """Обновление данных в таблице."""
        clients = self.model.get_all_clients()
        self.view.update_table(clients)


# ---------- ПРЕДСТАВЛЕНИЕ ---------- #
class MainView(tk.Tk, Observer):
    """Главное окно приложения."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Ломбард - Главное окно")
        self.geometry("600x400")

        # Таблица
        self.tree = ttk.Treeview(self, columns=("FIO", "Phone", "Pledges"), show="headings")
        self.tree.heading("FIO", text="ФИО")
        self.tree.heading("Phone", text="Телефон")
        self.tree.heading("Pledges", text="Количество залогов")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_table(self, clients):
        """Обновление данных таблицы."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for client in clients:
            self.tree.insert("", tk.END, values=(client["fio"], client["phone"], client["pledges"]))


# ---------- ЗАПУСК ---------- #
if __name__ == "__main__":
    client_repo = ClientRepository()  # Модель
    main_view = MainView(None)  # Создаём главное окно
    main_controller = MainController(main_view, client_repo)  # Контроллер связывает представление и модель
    main_view.mainloop()  # Запускаем главное окно

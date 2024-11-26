import sys
sys.path.append("C:/Users/Гамлет/Desktop/InfoSysDesign/Lab4")
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from model.client_model import ClientModel
from view.client_view import ClientView

class ClientPresenter(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.model = ClientModel()
        self.view = ClientView()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            clients = self.model.get_all_clients()
            html = self.view.render_template("templates/index.html", {"clients": clients})
            self._send_response(html)
        elif self.path.startswith("/details"):
            client_id = int(self._get_query_param("id"))
            client = self.model.get_client_by_id(client_id)
            html = self.view.render_template("templates/details.html", {"client": client})
            self._send_response(html)
        elif self.path.startswith("/form"):
            client_id = self._get_query_param("id")
            client = self.model.get_client_by_id(int(client_id)) if client_id else None
            html = self.view.render_template("templates/form.html", {"client": client})
            self._send_response(html)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = parse_qs(self.rfile.read(content_length).decode())
        print("POST data received:", post_data)  # Добавьте отладочный вывод

        if self.path == "/add":
            try:
                client_data = {
                    "fio": post_data["fio"][0],
                    "phone": post_data["phone"][0],
                    "address": post_data["address"][0],
                    "inn": post_data["inn"][0],
                    "birth_date": post_data.get("birth_date", [""])[0],  # Пустая строка по умолчанию
                }
                self.model.add_client(client_data)
                self._redirect("/")
            except KeyError as e:
                print(f"Ошибка: отсутствует ключ {e}")
            self._send_response("<h1>Ошибка: заполните все поля формы</h1>")
        elif self.path == "/edit":
            client_id = int(post_data["id"][0])
            client_data = {
                "fio": post_data["fio"][0],
                "phone": post_data["phone"][0],
                "address": post_data["address"][0],
                "inn": post_data["inn"][0],
                "birth_date": post_data["birth_date"][0],
            }
            self.model.update_client(client_id, client_data)
            self._redirect("/")
            
        elif self.path == "/delete":
            client_id = int(post_data["id"][0])
            self.model.delete_client(client_id)
            self._redirect("/")

    def _send_response(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _get_query_param(self, param):
        if "?" in self.path:
            query = self.path.split("?")[1]
            params = parse_qs(query)
            return params.get(param, [None])[0]
        return None

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), ClientPresenter)
    print("Сервер запущен на http://localhost:8080")
    server.serve_forever()

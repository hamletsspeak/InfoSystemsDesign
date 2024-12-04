import sys
sys.path.append('C:/Users/Гамлет/Desktop/InfoSysDesign/Lab4')

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from model.client_model import ClientModel
from view.client_view import ClientView
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ClientPresenter(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.model = ClientModel()
        self.view = ClientView()  # Используем класс, который реализует интерфейс IClientView
        super().__init__(*args, **kwargs)

    def do_GET(self):
        routes = {
            "/": self.handle_home,
            "/details": self.handle_details,
            "/form": self.handle_form,
        }
        handler = routes.get(self._get_route(), self.handle_not_found)
        handler()

    def do_POST(self):
        routes = {
            "/add": self.handle_add,
            "/edit": self.handle_edit,
            "/delete": self.handle_delete,
        }
        handler = routes.get(self.path, self.handle_not_found)
        handler()

    def handle_home(self):
        clients = self.model.get_all_clients()
        html = self.view.render_index(clients)  # Используем метод интерфейса
        self._send_response(html)

    def handle_details(self):
        client_id = self._get_query_param("id")
        if client_id:
            client = self.model.get_client_by_id(int(client_id))
            html = self.view.render_details(client)  # Используем метод интерфейса
            self._send_response(html)
        else:
            self.handle_bad_request("Client ID is missing.")

    def handle_form(self):
        client_id = self._get_query_param("id")
        client = self.model.get_client_by_id(int(client_id)) if client_id else None
        html = self.view.render_form(client)  # Используем метод интерфейса
        self._send_response(html)

    def handle_add(self):
        try:
            post_data = self._parse_post_data()
            client_data = self._extract_client_data(post_data)
            self.model.add_client(client_data)
            self._redirect("/")
        except KeyError as e:
            self.handle_bad_request(f"Missing form field: {e}")

    def handle_edit(self):
        try:
            post_data = self._parse_post_data()
            client_id = int(post_data["id"][0])
            client_data = self._extract_client_data(post_data)
            self.model.update_client(client_id, client_data)
            self._redirect("/")
        except Exception as e:
            logging.error(f"Error updating client: {e}")
            self.handle_bad_request("Failed to edit client.")

    def handle_delete(self):
        try:
            post_data = self._parse_post_data()
            client_id = int(post_data["id"][0])
            self.model.delete_client(client_id)
            self._redirect("/")
        except Exception as e:
            logging.error(f"Error deleting client: {e}")
            self.handle_bad_request("Failed to delete client.")

    def _send_response(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _get_query_param(self, param):
        try:
            if "?" in self.path:
                query = self.path.split("?")[1]
                params = parse_qs(query)
                return params.get(param, [None])[0]
            return None
        except Exception as e:
            logging.error(f"Failed to get query parameter '{param}': {e}")
            return None

    def _parse_post_data(self):
        content_length = int(self.headers['Content-Length'])
        return parse_qs(self.rfile.read(content_length).decode())

    def _extract_client_data(self, post_data):
        return {
            "fio": post_data["fio"][0],
            "phone": post_data["phone"][0],
            "address": post_data["address"][0],
            "inn": post_data["inn"][0],
            "birth_date": post_data.get("birth_date", [""])[0],
        }

    def handle_bad_request(self, message):
        logging.warning(f"Bad request: {message}")
        self._send_response(f"<h1>{message}</h1>", status=400)

    def handle_not_found(self):
        logging.warning(f"Route not found: {self.path}")
        self._send_response("<h1>404 Not Found</h1>", status=404)

    def _get_route(self):
        return self.path.split("?")[0]

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), ClientPresenter)
    logging.info("Server started at http://localhost:8080")
    server.serve_forever()

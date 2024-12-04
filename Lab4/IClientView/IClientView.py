from abc import ABC, abstractmethod

class IClientView(ABC):
    @abstractmethod
    def render_index(self, clients):
        pass

    @abstractmethod
    def render_details(self, client):
        pass

    @abstractmethod
    def render_form(self, client):
        pass

    @abstractmethod
    def render_template(self, template_path, context):
        pass

from jinja2 import Template

class ClientView:
    def render_template(self, template_path, context):
        full_path = f"C:/Users/Гамлет/Desktop/InfoSysDesign/Lab4/{template_path}"
        with open(full_path, 'r', encoding="utf-8") as file:
            template = Template(file.read())
        return template.render(context)

    def render_index(self, clients):
        """Рендеринг списка клиентов."""
        return self.render_template("templates/index.html", {"clients": clients})

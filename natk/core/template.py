import os
from pathlib import Path
class TemplateManager:
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or str(Path.home() / '.natk' / 'templates')
        os.makedirs(self.template_dir, exist_ok=True)
    def list_templates(self):
        templates = []
        for f in Path(self.template_dir).glob('*.j2'):
            templates.append(f.stem)
        return templates
    def get_template(self, name):
        path = Path(self.template_dir) / f'{name}.j2'
        if path.exists():
            return path.read_text()
        return None
    def save_template(self, name, content):
        path = Path(self.template_dir) / f'{name}.j2'
        with open(path, 'w') as f:
            f.write(content)
        return str(path)
    def render(self, template_name, variables):
        template = self.get_template(template_name)
        if not template:
            raise FileNotFoundError(f'Template {template_name} not found')
        result = template
        for key, value in variables.items():
            placeholder = '{{ ' + key + ' }}'
            result = result.replace(placeholder, str(value))
        return result
    def delete_template(self, name):
        path = Path(self.template_dir) / f'{name}.j2'
        if path.exists():
            path.unlink()
            return True
        return False

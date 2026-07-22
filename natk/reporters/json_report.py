import json
from natk.reporters.base import BaseReporter
class JSONReporter(BaseReporter):
    def generate(self, data, output_path):
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return output_path

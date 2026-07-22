import json
from datetime import datetime
class ReportGenerator:
    def __init__(self):
        self.sections = []
    def add_section(self, title, data):
        self.sections.append({"title": title, "data": data, "timestamp": datetime.utcnow().isoformat()})
    def to_json(self, path):
        report = {
            "generated": datetime.utcnow().isoformat(),
            "tool": "natk",
            "sections": self.sections,
        }
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path
    def to_text(self, path):
        lines = []
        lines.append("Network Automation Toolkit Report")
        lines.append("=" * 40)
        lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        lines.append("")
        for section in self.sections:
            lines.append(f"## {section['title']}")
            lines.append("")
            data = section["data"]
            if isinstance(data, list):
                for item in data:
                    lines.append(f"  - {item}")
            elif isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"  {key}: {value}")
            lines.append("")
        with open(path, "w") as f:
            f.write("\n".join(lines))
        return path
    def clear(self):
        self.sections = []

import datetime
from natk.reporters.base import BaseReporter
class HTMLReporter(BaseReporter):
    def generate(self, data, output_path):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rows = ""
        for item in data:
            host = item.get("host", "")
            vendor = item.get("vendor", "")
            status = item.get("status", "")
            rows += f"<tr><td>{host}</td><td>{vendor}</td><td>{status}</td></tr>"
        html = "<!DOCTYPE html><html><head><title>Report</title>"
        html += "<style>body{font-family:Arial;margin:20px}"
        html += "table{border-collapse:collapse;width:100%}"
        html += "th,td{border:1px solid #ddd;padding:8px;text-align:left}"
        html += "th{background:#333;color:white}</style></head><body>"
        html += f"<h1>Network Automation Report</h1><p>Generated: {timestamp}</p>"
        html += "<table><thead><tr><th>Host</th><th>Vendor</th><th>Status</th></tr></thead>"
        html += f"<tbody>{rows}</tbody></table></body></html>"
        with open(output_path, "w") as f:
            f.write(html)
        return output_path

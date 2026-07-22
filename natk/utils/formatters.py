def format_bytes(bytes_value):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"
def format_duration(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    else:
        return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"
def format_percentage(value, total):
    if total == 0:
        return "0%"
    return f"{(value / total * 100):.1f}%"
def format_table(data, headers=None):
    if not data:
        return "(empty)"
    if not headers:
        headers = list(data[0].keys())
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, h in enumerate(headers):
            val = str(row.get(h, ""))
            col_widths[i] = max(col_widths[i], len(val))
    lines = []
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("-+-".join("-" * w for w in col_widths))
    for row in data:
        lines.append(" | ".join(str(row.get(h, "")).ljust(col_widths[i]) for i, h in enumerate(headers)))
    return "\n".join(lines)
def pretty_print(obj, indent=0):
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(" " * indent + str(key) + ": ", end="")
            if isinstance(value, (dict, list)):
                print()
                pretty_print(value, indent + 2)
            else:
                print(str(value))
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                pretty_print(item, indent)
            else:
                print(" " * indent + "- " + str(item))

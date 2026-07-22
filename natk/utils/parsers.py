import re
def parse_mikrotik_export(text):
    sections = {}
    current_section = None
    current_lines = []
    for line in text.splitlines():
        if line.startswith("/"):
            if current_section and current_lines:
                sections[current_section] = "\n".join(current_lines)
            current_section = line.strip()
            current_lines = []
        elif current_section:
            current_lines.append(line)
    if current_section and current_lines:
        sections[current_section] = "\n".join(current_lines)
    return sections
def parse_ip(ip_string):
    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", ip_string)
    return match.group(1) if match else None
def parse_uptime(uptime_string):
    parts = uptime_string.split()
    total_seconds = 0
    i = 0
    while i < len(parts):
        if parts[i].isdigit() and i + 1 < len(parts):
            value = int(parts[i])
            unit = parts[i + 1].lower()
            if unit.startswith("week"):
                total_seconds += value * 7 * 86400
            elif unit.startswith("day"):
                total_seconds += value * 86400
            elif unit.startswith("hour"):
                total_seconds += value * 3600
            elif unit.startswith("minute"):
                total_seconds += value * 60
            elif unit.startswith("second"):
                total_seconds += value
            i += 2
        else:
            i += 1
    return total_seconds
def parse_ifconfig(output):
    interfaces = []
    current_iface = None
    for line in output.splitlines():
        iface_match = re.match(r"^(\S+):\s+flags=", line)
        if iface_match:
            if current_iface:
                interfaces.append(current_iface)
            current_iface = {"name": iface_match.group(1), "flags": [], "ip": None, "mac": None}
        if current_iface:
            ip_match = re.search(r"inet (\S+)", line)
            if ip_match:
                current_iface["ip"] = ip_match.group(1)
            mac_match = re.search(r"ether (\S+)", line)
            if mac_match:
                current_iface["mac"] = mac_match.group(1)
    if current_iface:
        interfaces.append(current_iface)
    return interfaces
def parse_hosts_file(content):
    hosts = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            hosts.append({"ip": parts[0], "hostnames": parts[1:]})
    return hosts

import ipaddress
import re
def validate_ip(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False
def validate_cidr(cidr):
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False
def validate_port(port):
    try:
        p = int(port)
        return 1 <= p <= 65535
    except (ValueError, TypeError):
        return False
def validate_hostname(hostname):
    if len(hostname) > 255:
        return False
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, hostname))
def validate_mac(mac):
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))
def sanitize_filename(name):
    return re.sub(r'[^\w\-\.]', '_', name)

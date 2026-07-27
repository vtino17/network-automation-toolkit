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
_TRAVERSAL = re.compile(r'\.{2,}')
_UNSAFE = re.compile(r'[^\w\-\.]')


def sanitize_filename(name, fallback='unnamed'):
    """Reduce an untrusted string to a name safe to join onto a directory.

    Replacing separators alone is not enough: '..' survives that step intact,
    and os.path.join(base, '..') resolves above `base`. Dot runs are therefore
    dropped before substitution. Names that end up referring to the directory
    itself ('', '.', '_') fall back to a fixed value, so a caller can never be
    handed a path that writes over the directory rather than into it.
    """
    cleaned = _UNSAFE.sub('_', _TRAVERSAL.sub('', name))
    if not cleaned.strip('._'):
        return fallback
    return cleaned

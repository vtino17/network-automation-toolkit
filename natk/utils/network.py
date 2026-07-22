import socket
import ipaddress
def ping_host(host, count=3):
    import subprocess
    import platform
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        result = subprocess.run(['ping', param, str(count), host], capture_output=True, timeout=30)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
def port_is_open(host, port, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
def scan_ports(host, ports, timeout=2):
    open_ports = []
    for port in ports:
        if port_is_open(host, port, timeout):
            open_ports.append(port)
    return open_ports
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'
def cidr_to_hosts(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(h) for h in network.hosts()]
    except ValueError:
        return []
def is_private_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private
    except ValueError:
        return False

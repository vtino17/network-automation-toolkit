import paramiko
import re
from natk.devices.base import BaseDevice
class LinuxDevice(BaseDevice):
    def __init__(self, hostname, ip, port=22, username="root", password=None):
        super().__init__(hostname, ip, port, username, password)
        self.vendor = "Linux"
        self.os_name = "Linux"
    def connect(self):
        self._connection = paramiko.SSHClient()
        self._connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connection.connect(
            self.ip, port=self.port,
            username=self.username, password=self.password,
            timeout=30, look_for_keys=False, allow_agent=False
        )
    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None
    def execute(self, command, timeout=60):
        if not self._connection:
            self.connect()
        stdin, stdout, stderr = self._connection.exec_command(command, timeout=timeout)
        output = stdout.read().decode("utf-8", errors="ignore")
        error = stderr.read().decode("utf-8", errors="ignore")
        return output
    def get_config(self):
        commands = [
            "cat /etc/network/interfaces 2>/dev/null || true",
            "iptables-save 2>/dev/null || true",
            "cat /etc/hostname",
            "cat /etc/resolv.conf",
            "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || true",
            "ip addr show 2>/dev/null || ifconfig -a 2>/dev/null || true",
        ]
        config_parts = []
        for cmd in commands:
            result = self.execute(cmd)
            config_parts.append(f"# {cmd}\n{result}")
        return "\n".join(config_parts)
    def get_facts(self):
        os_release = self.execute("cat /etc/os-release 2>/dev/null | head -5")
        kernel = self.execute("uname -r")
        hostname = self.execute("hostname")
        uptime = self.execute("uptime -p")
        mem = self.execute("free -h | grep Mem")
        cpu = self.execute("nproc")
        os_match = re.search(r'PRETTY_NAME="([^"]+)"', os_release)
        mem_match = re.search(r"(\S+)\s+(\S+)", mem) if mem else None
        self._facts = {
            "hostname": hostname.strip() or self.hostname,
            "vendor": "Linux",
            "os": os_match.group(1) if os_match else "Linux",
            "kernel": kernel.strip(),
            "uptime": uptime.strip(),
            "cpu_cores": cpu.strip(),
            "memory": mem_match.group(2) if mem_match else "unknown",
        }
        return self._facts
    def get_interfaces(self):
        output = self.execute("ip -json link 2>/dev/null || ip link show")
        interfaces = []
        try:
            import json
            data = json.loads(output)
            for iface in data:
                interfaces.append({
                    "name": iface.get("ifname", "unknown"),
                    "mac": iface.get("address", ""),
                    "status": "up" if iface.get("flags", []) else "down",
                })
        except (json.JSONDecodeError, ImportError):
            for line in output.split("\n"):
                if ":" in line and not line.startswith(" "):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        name = parts[1].strip().split("@")[0]
                        interfaces.append({"name": name, "status": "unknown"})
        return interfaces
    def get_services(self):
        return self.execute("systemctl list-units --type=service --state=running --no-pager")
    def get_disk_usage(self):
        return self.execute("df -h")
    def get_memory_usage(self):
        return self.execute("free -h")
    def get_process_list(self):
        return self.execute("ps aux --sort=-%cpu | head -20")
    def get_logs(self, service=None):
        if service:
            return self.execute(f"journalctl -u {service} --no-pager -n 50")
        return self.execute("journalctl --since '24 hours ago' --no-pager -n 100 | grep -i 'error\\|fail\\|denied' || true")
    def check_security_updates(self):
        return self.execute("apt list --upgradable 2>/dev/null | grep -i security || yum check-update --security 2>/dev/null || true")
    def get_firewall_status(self):
        return self.execute("ufw status 2>/dev/null || firewall-cmd --state 2>/dev/null || echo 'no firewall detected'")
    def ping_test(self, target, count=4):
        return self.execute(f"ping -c {count} {target}")

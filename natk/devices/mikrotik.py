import paramiko
import re
from natk.devices.base import BaseDevice
class MikroTikDevice(BaseDevice):
    def __init__(self, hostname, ip, port=22, username="admin", password=None):
        super().__init__(hostname, ip, port, username, password)
        self.vendor = "MikroTik"
        self.os_name = "RouterOS"
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
        if error and "error" in error.lower():
            raise RuntimeError(f"MikroTik error: {error}")
        return output
    def get_config(self):
        return self.execute("/export terse show-sensitive")
    def get_facts(self):
        identity = self.execute("/system identity print")
        resource = self.execute("/system resource print")
        uptime = self.execute("/system resource uptime")
        version_match = re.search(r"version:\s*(\S+)", resource)
        serial_match = re.search(r"serial-number:\s*(\S+)", resource)
        identity_match = re.search(r"name:\s*(\S+)", identity)
        uptime_match = re.search(r"uptime:\s*(.+)", uptime)
        self._facts = {
            "hostname": identity_match.group(1) if identity_match else self.hostname,
            "vendor": self.vendor,
            "os": self.os_name,
            "version": version_match.group(1) if version_match else "unknown",
            "serial": serial_match.group(1) if serial_match else "unknown",
            "uptime": uptime_match.group(1) if uptime_match else "unknown",
        }
        return self._facts
    def get_interfaces(self):
        output = self.execute("/interface print detail")
        interfaces = []
        current = {}
        for line in output.split("\n"):
            if line.startswith("Flags:"):
                continue
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 3:
                interfaces.append({
                    "name": parts[1] if len(parts) > 1 else "unknown",
                    "type": parts[2] if len(parts) > 2 else "unknown",
                    "running": "R" in line,
                })
        return interfaces
    def get_routes(self):
        output = self.execute("/ip route print detail")
        routes = []
        for line in output.split("\n"):
            if "dst-address" in line:
                routes.append(line.strip())
        return routes
    def get_firewall_rules(self):
        output = self.execute("/ip firewall filter print detail")
        return output.split("\n")
    def get_logs(self, lines=100):
        return self.execute(f"/log print where topics~'critical,error' limit={lines}")
    def backup_binary(self):
        identity = self._facts.get("hostname", self.hostname)
        result = self.execute(f"/system backup save name={identity}")
        return result
    def reboot(self, delay=60):
        return self.execute(f"/system reboot after={delay}")
    def ping_test(self, target, count=4):
        return self.execute(f"/ping {target} count={count}")

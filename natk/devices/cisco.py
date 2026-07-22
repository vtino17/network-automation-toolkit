import paramiko
import re
from natk.devices.base import BaseDevice
class CiscoDevice(BaseDevice):
    def __init__(self, hostname, ip, port=22, username="admin", password=None, enable_password=None):
        super().__init__(hostname, ip, port, username, password)
        self.enable_password = enable_password
        self.vendor = "Cisco"
        self.os_name = "IOS"
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
        channel = self._connection.invoke_shell()
        channel.settimeout(timeout)
        if self.enable_password:
            channel.send("enable\n")
            channel.recv(1024)
            channel.send(f"{self.enable_password}\n")
            channel.recv(1024)
        channel.send("terminal length 0\n")
        channel.recv(1024)
        channel.send(f"{command}\n")
        import time
        time.sleep(2)
        output = b""
        while channel.recv_ready():
            try:
                chunk = channel.recv(65535)
                if not chunk:
                    break
                output += chunk
            except Exception:
                break
        channel.close()
        return output.decode("utf-8", errors="ignore")
    def get_config(self):
        return self.execute("show running-config")
    def get_facts(self):
        version = self.execute("show version")
        hostname_match = re.search(r"(\S+) uptime", version)
        version_match = re.search(r"Version (\S+)", version)
        serial_match = re.search(r"System serial number\s*:\s*(\S+)", version)
        self._facts = {
            "hostname": hostname_match.group(1) if hostname_match else self.hostname,
            "vendor": self.vendor,
            "os": self.os_name,
            "version": version_match.group(1) if version_match else "unknown",
            "serial": serial_match.group(1) if serial_match else "unknown",
            "uptime": "unknown",
        }
        return self._facts
    def get_interfaces(self):
        output = self.execute("show interfaces summary")
        interfaces = []
        for line in output.split("\n"):
            if line and not line.startswith(" ") and "*" not in line:
                parts = line.split()
                if parts:
                    interfaces.append({"name": parts[0], "status": "unknown"})
        return interfaces
    def get_vlan(self):
        return self.execute("show vlan brief")
    def get_mac_table(self):
        return self.execute("show mac address-table")
    def get_arp(self):
        return self.execute("show ip arp")
    def get_logs(self):
        return self.execute("show logging")
    def get_running_config(self):
        return self.execute("show running-config")
    def get_startup_config(self):
        return self.execute("show startup-config")
    def save_config(self):
        return self.execute("copy running-config startup-config")
    def ping_test(self, target):
        return self.execute(f"ping {target} repeat 4")

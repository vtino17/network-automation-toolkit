import paramiko
import re
import ssl
import json
import urllib.request
import urllib.parse
from natk.devices.base import BaseDevice
class PFSenseDevice(BaseDevice):
    def __init__(self, hostname, ip, port=22, username="admin", password=None):
        super().__init__(hostname, ip, port, username, password)
        self.vendor = "pfSense"
        self.os_name = "FreeBSD"
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
        if error:
            raise RuntimeError(f"pfSense error: {error}")
        return output
    def get_config(self):
        return self.execute("cat /cf/conf/config.xml")
    def get_facts(self):
        version = self.execute("cat /etc/version")
        hostname = self.execute("cat /etc/hostname")
        uptime = self.execute("uptime")
        hostname_match = re.search(r"(\S+)", hostname)
        self._facts = {
            "hostname": hostname_match.group(1) if hostname_match else self.hostname,
            "vendor": self.vendor,
            "os": self.os_name,
            "version": version.strip(),
            "uptime": uptime.strip(),
        }
        return self._facts
    def get_interfaces(self):
        output = self.execute("ifconfig -l")
        interfaces = output.strip().split()
        result = []
        for iface in interfaces:
            if iface in ("lo0", "pfsync0"):
                continue
            detail = self.execute(f"ifconfig {iface}")
            inet_match = re.search(r"inet (\S+)", detail)
            status_match = re.search(r"status: (\S+)", detail)
            result.append({
                "name": iface,
                "ip": inet_match.group(1) if inet_match else None,
                "status": status_match.group(1) if status_match else "unknown",
            })
        return result
    def get_firewall_rules(self):
        output = self.execute("cat /cf/conf/config.xml")
        import xml.etree.ElementTree as ET
        rules = []
        try:
            root = ET.fromstring(output)
            for rule in root.iter("rule"):
                desc = rule.find("descr")
                proto = rule.find("protocol")
                dstport = rule.find("destination/port")
                rules.append({
                    "description": desc.text if desc is not None else "",
                    "protocol": proto.text if proto is not None else "",
                    "port": dstport.text if dstport is not None else "",
                })
        except ET.ParseError:
            pass
        return rules
    def get_states(self):
        output = self.execute("pfctl -s states | wc -l")
        return int(output.strip())
    def get_traffic(self, interface="wan"):
        output = self.execute(f"netstat -I {interface} -b -w 60 2 2>/dev/null | tail -1")
        parts = output.split()
        if len(parts) >= 10:
            return {"in_bytes": parts[6], "out_bytes": parts[9]}
        return {"in_bytes": "0", "out_bytes": "0"}
    def get_dhcp_leases(self):
        return self.execute("cat /var/dhcpd/var/db/dhcpd.leases")
    def get_logs(self, lines=50):
        return self.execute(f"tail -{lines} /var/log/filter.log")
    def api_request(self, endpoint, method="GET"):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        url = f"https://{self.ip}/api/v1/{endpoint}"
        req = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30, context=context) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

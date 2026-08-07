import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
class BackupManager:
    def __init__(self, output_dir="./backups", parallel=5, compress=False):
        self.output_dir = Path(output_dir)
        self.parallel = parallel
        self.compress = compress
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def run(self, hosts=None):
        from natk.core.inventory import InventoryManager
        inv = InventoryManager()
        devices = inv.list_devices()
        if hosts:
            devices = [d for d in devices if d["hostname"] in hosts or d.get("ip") in hosts]
        results = []
        with ThreadPoolExecutor(max_workers=self.parallel) as executor:
            futures = {executor.submit(self._backup_device, d): d for d in devices}
            for future in as_completed(futures):
                device = futures[future]
                try:
                    result = future.result()
                    if result["success"]:
                        inv.update_status(device["hostname"], "backed_up")
                    results.append(result)
                except Exception as e:
                    results.append({"host": device["hostname"], "success": False, "error": str(e)})
        return results
    def _backup_device(self, device):
        hostname = self._safe_component(device["hostname"], "hostname")
        vendor = self._safe_component(device.get("vendor", "unknown"), "vendor")
        ip = device.get("ip", hostname)
        port = device.get("port", 22)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        vendor_dir = self.output_dir / vendor
        vendor_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{hostname}_{timestamp}.cfg"
        filepath = vendor_dir / filename
        try:
            if vendor == "mikrotik":
                config = self._backup_mikrotik(ip, port)
            elif vendor == "cisco":
                config = self._backup_cisco(ip, port)
            elif vendor == "pfsense":
                config = self._backup_pfsense(ip)
            elif vendor == "linux":
                config = self._backup_linux(ip, port)
            else:
                config = self._backup_generic(ip, port)
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(filepath, flags, 0o600)
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as f:
                f.write(config)
            return {
                "host": hostname,
                "vendor": vendor,
                "success": True,
                "path": str(filepath),
                "size": len(config),
                "timestamp": timestamp,
            }
        except Exception as e:
            return {
                "host": hostname,
                "vendor": vendor,
                "success": False,
                "error": str(e),
            }
    @staticmethod
    def _safe_component(value, field):
        text = str(value)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", text):
            raise ValueError(f"Invalid {field}: expected a safe filename component")
        return text
    def _exec_ssh(self, ip, port, username, password, command):
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username=username, password=password, timeout=30)
        stdin, stdout, stderr = client.exec_command(command, timeout=60)
        output = stdout.read().decode("utf-8", errors="ignore")
        error = stderr.read().decode("utf-8", errors="ignore")
        client.close()
        if error:
            raise RuntimeError(f"SSH command error: {error}")
        return output
    def _backup_mikrotik(self, ip, port):
        config = self._exec_ssh(ip, port, "admin", "", "/export terse show-sensitive")
        return config
    def _backup_cisco(self, ip, port):
        config = self._exec_ssh(ip, port, "admin", "", "show running-config")
        return config
    def _backup_pfsense(self, ip):
        import urllib.request
        url = f"https://{ip}/diag_backup.php?download=config"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.read().decode("utf-8")
    def _backup_linux(self, ip, port):
        commands = [
            "cat /etc/network/interfaces 2>/dev/null",
            "iptables-save 2>/dev/null",
            "cat /etc/hostname",
            "cat /etc/resolv.conf",
            "netstat -tlnp 2>/dev/null || ss -tlnp",
            "cat /etc/ssh/sshd_config 2>/dev/null",
        ]
        output = []
        for cmd in commands:
            try:
                result = self._exec_ssh(ip, port, "root", "", cmd)
                output.append(f"# {cmd}\n{result}")
            except Exception:
                pass
        return "\n".join(output)
    def _backup_generic(self, ip, port):
        return self._backup_linux(ip, port)
    def list_backups(self, host=None):
        backups = []
        for path in self.output_dir.rglob("*.cfg"):
            if host and host not in path.name:
                continue
            backups.append({
                "path": str(path),
                "host": path.stem.split("_")[0],
                "timestamp": path.stem.split("_")[1] if "_" in path.stem else "unknown",
                "size": path.stat().st_size,
            })
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

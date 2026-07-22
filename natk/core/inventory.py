import json
import csv
from datetime import datetime
class InventoryManager:
    def __init__(self, inventory_file=None):
        self.inventory_file = inventory_file or "inventory.json"
        self.devices = []
        self._load()
    def _load(self):
        try:
            with open(self.inventory_file) as f:
                self.devices = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.devices = []
    def _save(self):
        with open(self.inventory_file, "w") as f:
            json.dump(self.devices, f, indent=2)
    def list_devices(self):
        return self.devices
    def add_device(self, hostname, vendor, ip=None, port=22, auth_method="password", tags=None):
        device = {
            "hostname": hostname,
            "vendor": vendor,
            "ip": ip or hostname,
            "port": port,
            "auth_method": auth_method,
            "tags": tags or [],
            "added": datetime.utcnow().isoformat(),
            "last_seen": None,
            "status": "unknown",
            "os_version": None,
            "serial": None,
        }
        existing = [d for d in self.devices if d["hostname"] == hostname]
        if existing:
            existing[0].update(device)
            existing[0]["updated"] = datetime.utcnow().isoformat()
        else:
            self.devices.append(device)
        self._save()
        return device
    def remove_device(self, hostname):
        self.devices = [d for d in self.devices if d["hostname"] != hostname]
        self._save()
    def get_device(self, hostname):
        for d in self.devices:
            if d["hostname"] == hostname or d.get("ip") == hostname:
                return d
        return None
    def get_by_vendor(self, vendor):
        return [d for d in self.devices if d["vendor"] == vendor]
    def get_by_tag(self, tag):
        return [d for d in self.devices if tag in d.get("tags", [])]
    def update_status(self, hostname, status, os_version=None, serial=None):
        device = self.get_device(hostname)
        if device:
            device["status"] = status
            device["last_seen"] = datetime.utcnow().isoformat()
            if os_version:
                device["os_version"] = os_version
            if serial:
                device["serial"] = serial
            self._save()
    def export_json(self, path=None):
        output = path or "inventory_export.json"
        with open(output, "w") as f:
            json.dump(self.devices, f, indent=2)
        return output
    def export_csv(self, path=None):
        output = path or "inventory_export.csv"
        if not self.devices:
            return output
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.devices[0].keys())
            writer.writeheader()
            writer.writerows(self.devices)
        return output
    def count(self):
        return len(self.devices)
    def summary(self):
        vendors = {}
        statuses = {}
        for d in self.devices:
            v = d.get("vendor", "unknown")
            vendors[v] = vendors.get(v, 0) + 1
            s = d.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total": len(self.devices),
            "by_vendor": vendors,
            "by_status": statuses,
        }

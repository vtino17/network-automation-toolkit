import tempfile
import os
import json
from natk.core.inventory import InventoryManager
class TestInventoryManager:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        self.tmp.write("[]")
        self.tmp.close()
        self.inv = InventoryManager(self.tmp.name)
    def teardown_method(self):
        os.unlink(self.tmp.name)
    def test_add_device(self):
        d = self.inv.add_device("router1", "mikrotik", "10.0.0.1")
        assert d["hostname"] == "router1"
        assert d["vendor"] == "mikrotik"
        assert self.inv.count() == 1
    def test_list_devices(self):
        self.inv.add_device("r1", "mikrotik")
        self.inv.add_device("r2", "cisco")
        assert len(self.inv.list_devices()) == 2
    def test_remove_device(self):
        self.inv.add_device("r1", "mikrotik")
        self.inv.remove_device("r1")
        assert self.inv.count() == 0
    def test_get_device_by_hostname(self):
        self.inv.add_device("router1", "mikrotik", "10.0.0.1")
        d = self.inv.get_device("router1")
        assert d is not None
        assert d["ip"] == "10.0.0.1"
    def test_get_device_by_ip(self):
        self.inv.add_device("router1", "mikrotik", "10.0.0.1")
        d = self.inv.get_device("10.0.0.1")
        assert d is not None
    def test_get_by_vendor(self):
        self.inv.add_device("r1", "mikrotik")
        self.inv.add_device("r2", "cisco")
        self.inv.add_device("r3", "mikrotik")
        assert len(self.inv.get_by_vendor("mikrotik")) == 2
    def test_summary(self):
        self.inv.add_device("r1", "mikrotik")
        self.inv.add_device("r2", "cisco")
        s = self.inv.summary()
        assert s["total"] == 2
        assert s["by_vendor"]["mikrotik"] == 1
        assert s["by_vendor"]["cisco"] == 1
    def test_export_json(self):
        self.inv.add_device("r1", "mikrotik")
        path = self.inv.export_json()
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 1
        os.unlink(path)
    def test_update_status(self):
        self.inv.add_device("r1", "mikrotik")
        self.inv.update_status("r1", "online", "7.10", "SN001")
        d = self.inv.get_device("r1")
        assert d["status"] == "online"
        assert d["os_version"] == "7.10"
    def test_remove_nonexistent(self):
        self.inv.remove_device("ghost")
        assert self.inv.count() == 0

import tempfile
import os
import json
from natk.core.config import Config
class TestConfig:
    def test_defaults(self):
        c = Config()
        assert c.get("ssh_port") == 22
        assert c.get("parallel_jobs") == 5
        assert c.get("backup_dir") == "./backups"
    def test_load_json(self):
        data = {"ssh_port": 2222, "log_level": "DEBUG"}
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        json.dump(data, tmp)
        tmp.close()
        c = Config(tmp.name)
        assert c.get("ssh_port") == 2222
        assert c.get("log_level") == "DEBUG"
        os.unlink(tmp.name)
    def test_custom_value(self):
        c = Config()
        c.set("custom_key", "custom_value")
        assert c.get("custom_key") == "custom_value"
    def test_contains(self):
        c = Config()
        assert "ssh_port" in c
        assert "nonexistent" not in c
    def test_get_default(self):
        c = Config()
        assert c.get("undefined_key", "fallback") == "fallback"
    def test_save(self):
        c = Config()
        c.set("test_key", "test_value")
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        tmp.close()
        c.save(tmp.name)
        c2 = Config(tmp.name)
        assert c2.get("test_key") == "test_value"
        os.unlink(tmp.name)
    def test_config_not_found(self):
        try:
            Config("/nonexistent/config.json")
            assert False
        except FileNotFoundError:
            assert True

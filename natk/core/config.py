import json
import os
from pathlib import Path
class Config:
    DEFAULTS = {
        "inventory_file": "inventory.json",
        "backup_dir": "./backups",
        "ssh_port": 22,
        "ssh_timeout": 30,
        "ssh_user": "admin",
        "parallel_jobs": 5,
        "log_level": "INFO",
        "log_file": None,
        "compliance_policy": "policies/default.json",
        "retry_count": 3,
        "retry_delay": 5,
        "verify_ssl": False,
    }
    def __init__(self, config_path=None):
        self._data = dict(self.DEFAULTS)
        if config_path:
            self.load(config_path)
        self._apply_env_overrides()
    def load(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path) as f:
            if path.suffix == ".json":
                data = json.load(f)
            elif path.suffix in (".yml", ".yaml"):
                import yaml
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        self._data.update(data)
    def _apply_env_overrides(self):
        overrides = {
            "NATK_INVENTORY": "inventory_file",
            "NATK_BACKUP_DIR": "backup_dir",
            "NATK_SSH_PORT": "ssh_port",
            "NATK_SSH_USER": "ssh_user",
            "NATK_SSH_TIMEOUT": "ssh_timeout",
            "NATK_LOG_LEVEL": "log_level",
            "NATK_PARALLEL": "parallel_jobs",
        }
        for env_key, config_key in overrides.items():
            if env_key in os.environ:
                value = os.environ[env_key]
                if config_key in ("ssh_port", "ssh_timeout", "parallel_jobs", "retry_count", "retry_delay"):
                    value = int(value)
                self._data[config_key] = value
    def get(self, key, default=None):
        return self._data.get(key, default)
    def set(self, key, value):
        self._data[key] = value
    def save(self, path):
        path = Path(path)
        with open(path, "w") as f:
            if path.suffix == ".json":
                json.dump(self._data, f, indent=2)
            elif path.suffix in (".yml", ".yaml"):
                import yaml
                yaml.dump(self._data, f)
    def __getitem__(self, key):
        return self._data[key]
    def __contains__(self, key):
        return key in self._data

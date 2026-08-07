import os
import pytest

from natk.core.backup import BackupManager


def test_backup_succeeds_and_is_private(tmp_path, monkeypatch):
    manager = BackupManager(tmp_path)
    monkeypatch.setattr(manager, "_backup_mikrotik", lambda ip, port: "secret config")

    result = manager._backup_device(
        {"hostname": "router-1", "vendor": "mikrotik", "ip": "192.0.2.1"}
    )

    assert result["success"] is True
    assert os.stat(result["path"]).st_mode & 0o777 == 0o600


def test_backup_rejects_inventory_path_traversal(tmp_path):
    manager = BackupManager(tmp_path)

    with pytest.raises(ValueError, match="Invalid hostname"):
        manager._backup_device(
            {"hostname": "../../outside", "vendor": "mikrotik", "ip": "192.0.2.1"}
        )
    assert not (tmp_path.parent / "outside").exists()

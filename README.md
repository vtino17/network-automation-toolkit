# Network Automation Toolkit

Python framework for automated network device management. Supports configuration backup, compliance auditing, inventory tracking, and multi-vendor device operations.

## Supported Vendors

- MikroTik RouterOS
- Cisco IOS/IOS-XE
- pfSense/OPNsense
- Linux servers

## Quick Start

```bash
pip install -r requirements.txt
python -m natk.cli inventory list
python -m natk.cli backup --hosts router1 switch1
python -m natk.cli check --policy policy.json
```

## Commands

- `inventory` - Manage device inventory (list, add, remove, export)
- `backup` - Backup device configurations
- `check` - Run compliance checks
- `diff` - Compare configuration revisions
- `schedule` - Schedule recurring tasks

## License

MIT

# Network Automation Toolkit

[![CI](https://github.com/vtino17/network-automation-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/vtino17/network-automation-toolkit/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/vtino17/network-automation-toolkit?style=flat-square)](LICENSE)

Network Automation Toolkit (`natk`) is a Python package for repeatable multi-vendor network operations. It provides device abstractions, inventory management, configuration backup and comparison, compliance checks, templating, scheduling, and report generation.

## Supported Platforms

- Cisco IOS
- MikroTik RouterOS
- Linux hosts over SSH
- pfSense

## Capabilities

- Maintain inventories and device connection settings.
- Back up device configurations and compare revisions.
- Validate configuration baselines with reusable compliance checks.
- Render and apply configuration templates.
- Produce JSON and HTML reports for automation results.
- Schedule recurring network tasks.

## Installation

```bash
git clone https://github.com/vtino17/network-automation-toolkit.git
cd network-automation-toolkit
python -m pip install -e .
```

For development and testing:

```bash
python -m pip install -e ".[dev]"
```

## Development

Run the automated test suite before opening a pull request:

```bash
pytest
```

## Project Layout

```text
natk/
  core/        inventory, backups, compliance, diffs, templates, scheduling
  devices/     Cisco, Linux, MikroTik, and pfSense device adapters
  reporters/   JSON and HTML result renderers
  utils/       SSH, validation, parsing, logging, and network helpers
tests/         unit tests
```

## Security

Do not commit device credentials, API tokens, or production configuration exports. See [SECURITY.md](SECURITY.md) for responsible disclosure guidance.

## License

MIT

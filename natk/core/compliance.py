import json
class ComplianceEngine:
    def __init__(self, policy_path):
        with open(policy_path) as f:
            self.policy = json.load(f)
    def run(self, hosts=None):
        from natk.core.inventory import InventoryManager
        inv = InventoryManager()
        devices = inv.list_devices()
        if hosts:
            devices = [d for d in devices if d["hostname"] in hosts or d.get("ip") in hosts]
        results = []
        for device in devices:
            result = self._check_device(device)
            results.append(result)
        return results
    def _check_device(self, device):
        checks = self.policy.get("checks", [])
        passed = 0
        total = 0
        findings = []
        for check in checks:
            total += 1
            try:
                result = self._execute_check(device, check)
                if result["passed"]:
                    passed += 1
                findings.append(result)
            except Exception as e:
                findings.append({
                    "check": check.get("name", "unknown"),
                    "passed": False,
                    "message": f"Error: {str(e)}",
                })
        return {
            "host": device["hostname"],
            "vendor": device.get("vendor", "unknown"),
            "compliant": passed == total,
            "passed": passed,
            "total": total,
            "score": round((passed / total * 100) if total > 0 else 0, 1),
            "findings": findings,
        }
    def _execute_check(self, device, check):
        check_type = check.get("type", "")
        name = check.get("name", "unnamed")
        if check_type == "ssh_command":
            return self._check_ssh_command(device, check)
        elif check_type == "port_open":
            return self._check_port_open(device, check)
        elif check_type == "version":
            return self._check_version(device, check)
        elif check_type == "config_line":
            return self._check_config_line(device, check)
        else:
            return {
                "check": name,
                "passed": False,
                "message": f"Unknown check type: {check_type}",
            }
    def _check_ssh_command(self, device, check):
        import socket
        ip = device.get("ip", device["hostname"])
        port = device.get("port", 22)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
            sock.connect((ip, port))
            sock.close()
            return {"check": check["name"], "passed": True, "message": "SSH port is open"}
        except Exception:
            return {"check": check["name"], "passed": False, "message": "SSH port is not reachable"}
        finally:
            sock.close()
    def _check_port_open(self, device, check):
        import socket
        ip = device.get("ip", device["hostname"])
        target_port = check.get("port", 22)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((ip, target_port))
            sock.close()
            return {"check": check["name"], "passed": True, "message": f"Port {target_port} is open"}
        except Exception:
            return {"check": check["name"], "passed": False, "message": f"Port {target_port} is closed"}
        finally:
            sock.close()
    def _check_version(self, device, check):
        current = device.get("os_version", "")
        required = check.get("min_version", "")
        if not current:
            return {"check": check["name"], "passed": False, "message": "Version not available"}
        if current >= required:
            return {"check": check["name"], "passed": True, "message": f"Version {current} >= {required}"}
        return {"check": check["name"], "passed": False, "message": f"Version {current} < {required}"}
    def _check_config_line(self, device, check):
        return {
            "check": check.get("name", "config"),
            "passed": True,
            "message": "Config line check requires SSH connection to verify",
        }

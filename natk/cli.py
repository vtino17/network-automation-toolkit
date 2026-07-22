import argparse
import sys
from pathlib import Path
def build_parser():
    parser = argparse.ArgumentParser(description="Network Automation Toolkit")
    sub = parser.add_subparsers(dest="command")
    inv = sub.add_parser("inventory", help="Manage device inventory")
    inv.add_argument("action", choices=["list", "add", "remove", "import", "export"])
    inv.add_argument("--file", "-f", help="Inventory file path")
    inv.add_argument("--host", help="Device hostname or IP")
    inv.add_argument("--vendor", choices=["mikrotik", "cisco", "pfsense", "linux"])
    inv.add_argument("--output", "-o", help="Output format (json, yaml)")
    bk = sub.add_parser("backup", help="Backup device configurations")
    bk.add_argument("--hosts", "-H", nargs="+", help="Specific hosts to backup")
    bk.add_argument("--output-dir", "-o", default="./backups")
    bk.add_argument("--compress", "-c", action="store_true")
    bk.add_argument("--parallel", "-p", type=int, default=5)
    chk = sub.add_parser("check", help="Run compliance checks")
    chk.add_argument("--policy", "-p", required=True, help="Compliance policy file")
    chk.add_argument("--hosts", "-H", nargs="+", help="Hosts to check")
    chk.add_argument("--report", "-r", choices=["html", "json", "cli"], default="cli")
    diff = sub.add_parser("diff", help="Compare device configurations")
    diff.add_argument("host", help="Hostname or IP")
    diff.add_argument("--revision1", "-1", help="First revision")
    diff.add_argument("--revision2", "-2", help="Second revision")
    sched = sub.add_parser("schedule", help="Schedule recurring tasks")
    sched.add_argument("task", choices=["backup", "check"])
    sched.add_argument("--interval", choices=["hourly", "daily", "weekly", "monthly"], default="daily")
    sched.add_argument("--time", default="02:00")
    return parser
def entry_point():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if args.command == "inventory":
        from natk.core.inventory import InventoryManager
        mgr = InventoryManager()
        if args.action == "list":
            devices = mgr.list_devices()
            for d in devices:
                print(f"{d['hostname']:20s} {d['vendor']:10s} {d['ip']:15s} {d['status']:10s}")
        elif args.action == "add":
            mgr.add_device(args.host, args.vendor)
        elif args.action == "remove":
            mgr.remove_device(args.host)
        elif args.action == "export":
            path = mgr.export_json(args.output or "inventory.json")
            print(f"Inventory exported to {path}")
    elif args.command == "backup":
        from natk.core.backup import BackupManager
        bm = BackupManager(output_dir=args.output_dir, parallel=args.parallel)
        results = bm.run(args.hosts)
        print(f"Backup completed: {len(results)} devices")
        for r in results:
            status = "\u2713" if r["success"] else "\u2717"
            print(f"  {status} {r['host']}: {r.get('path', r.get('error', 'unknown'))}")
    elif args.command == "check":
        from natk.core.compliance import ComplianceEngine
        engine = ComplianceEngine(args.policy)
        results = engine.run(args.hosts)
        if args.report == "cli":
            for r in results:
                status = "PASS" if r["compliant"] else "FAIL"
                print(f"[{status}] {r['host']}: {r['passed']}/{r['total']} checks passed")
                for finding in r.get("findings", []):
                    if not finding["passed"]:
                        print(f"       {finding['check']}: {finding['message']}")
        elif args.report == "json":
            import json
            print(json.dumps(results, indent=2))
    elif args.command == "diff":
        from natk.core.diff import ConfigDiffer
        differ = ConfigDiffer()
        diff_result = differ.compare(args.host, args.revision1, args.revision2)
        for line in diff_result:
            print(line)
    elif args.command == "schedule":
        from natk.core.scheduler import Scheduler
        sched = Scheduler()
        sched.add_task(args.task, args.interval, args.time)
        print(f"Scheduled {args.task} ({args.interval}) at {args.time}")
if __name__ == "__main__":
    entry_point()

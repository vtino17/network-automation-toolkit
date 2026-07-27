import json
import datetime
class Database:
    def __init__(self, path='natk.db'):
        self.path = path
        self._data = {'devices': [], 'backups': [], 'checks': [], 'schedules': []}
    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self._data, f, indent=2)
    def load(self):
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    def add_backup_record(self, host, path, status):
        self._data['backups'].append({
            'host': host, 'path': path, 'status': status,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        self.save()
    def add_check_record(self, host, policy, passed, total):
        self._data['checks'].append({
            'host': host, 'policy': policy,
            'passed': passed, 'total': total,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        self.save()
    def get_backups(self, limit=50):
        return self._data['backups'][-limit:]
    def get_checks(self, limit=50):
        return self._data['checks'][-limit:]
    def get_stats(self):
        total_backups = len(self._data['backups'])
        total_checks = len(self._data['checks'])
        successful = sum(1 for b in self._data['backups'] if b.get('status') == 'success')
        return {
            'total_backups': total_backups,
            'total_checks': total_checks,
            'successful_backups': successful,
            'failed_backups': total_backups - successful,
        }

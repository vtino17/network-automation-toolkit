import json
import datetime
from pathlib import Path
class Scheduler:
    def __init__(self, path='schedules.json'):
        self.path = path
        self.tasks = []
        self._load()
    def _load(self):
        try:
            with open(self.path) as f:
                self.tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    def add_task(self, task_type, interval, time='02:00'):
        task = {
            'id': len(self.tasks) + 1,
            'type': task_type,
            'interval': interval,
            'time': time,
            'created': datetime.datetime.utcnow().isoformat(),
            'last_run': None,
            'next_run': self._calculate_next(interval, time),
            'enabled': True,
        }
        self.tasks.append(task)
        self._save()
        return task
    def remove_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self._save()
    def list_tasks(self):
        return self.tasks
    def get_due_tasks(self):
        now = datetime.datetime.utcnow()
        return [t for t in self.tasks if t['enabled'] and t.get('next_run') and datetime.datetime.fromisoformat(t['next_run']) <= now]
    def mark_run(self, task_id):
        for t in self.tasks:
            if t['id'] == task_id:
                t['last_run'] = datetime.datetime.utcnow().isoformat()
                t['next_run'] = self._calculate_next(t['interval'], t.get('time', '02:00'))
                break
        self._save()
    def _calculate_next(self, interval, time_str):
        now = datetime.datetime.utcnow()
        hour, minute = map(int, time_str.split(':'))
        base = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if base <= now:
            if interval == 'hourly':
                base = base + datetime.timedelta(hours=1)
            elif interval == 'daily':
                base = base + datetime.timedelta(days=1)
            elif interval == 'weekly':
                base = base + datetime.timedelta(weeks=1)
            elif interval == 'monthly':
                month = base.month + 1
                year = base.year
                if month > 12:
                    month = 1
                    year += 1
                base = base.replace(year=year, month=month)
        return base.isoformat()

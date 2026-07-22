import difflib
class ConfigDiffer:
    def compare(self, host, rev1, rev2):
        config1 = self._load_config(host, rev1)
        config2 = self._load_config(host, rev2)
        differ = difflib.unified_diff(
            config1.splitlines(keepends=True),
            config2.splitlines(keepends=True),
            fromfile=f'{host}:{rev1}',
            tofile=f'{host}:{rev2}'
        )
        return list(differ)
    def _load_config(self, host, revision):
        from pathlib import Path
        path = Path(f'./backups/{host}_{revision}.cfg')
        if path.exists():
            return path.read_text()
        return f'# Revision {revision} not found'
    def has_changes(self, host, rev1, rev2):
        return len(self.compare(host, rev1, rev2)) > 0
    def summary(self, host, rev1, rev2):
        diff = self.compare(host, rev1, rev2)
        added = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
        removed = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
        return {'added': added, 'removed': removed, 'total': len(diff)}

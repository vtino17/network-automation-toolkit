import json
import http.server
import urllib.parse
class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/health':
            self._json({'status': 'ok'})
        elif parsed.path == '/inventory':
            from natk.core.inventory import InventoryManager
            inv = InventoryManager()
            self._json(inv.list_devices())
        elif parsed.path.startswith('/backup/'):
            host = parsed.path.split('/')[-1]
            from natk.core.backup import BackupManager
            bm = BackupManager()
            backups = bm.list_backups(host)
            self._json(backups)
        else:
            self._json({'error': 'not found'}, 404)
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        data = json.loads(body)
        if parsed.path == '/backup':
            from natk.core.backup import BackupManager
            bm = BackupManager()
            hosts = data.get('hosts')
            results = bm.run(hosts)
            self._json(results)
        elif parsed.path == '/check':
            from natk.core.compliance import ComplianceEngine
            policy = data.get('policy', 'policy.json')
            engine = ComplianceEngine(policy)
            results = engine.run(data.get('hosts'))
            self._json(results)
        else:
            self._json({'error': 'not found'}, 404)
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
def start_api(port=8080):
    server = http.server.HTTPServer(('0.0.0.0', port), APIHandler)
    print(f'NATK API running on port {port}')
    server.serve_forever()

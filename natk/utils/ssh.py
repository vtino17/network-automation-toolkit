import paramiko
import socket
class SSHClient:
    def __init__(self, host, port=22, username='admin', password=None, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self._client = None
    def connect(self):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            self.host, port=self.port,
            username=self.username, password=self.password,
            timeout=self.timeout, look_for_keys=False, allow_agent=False
        )
    def run(self, command, timeout=60):
        if not self._client:
            self.connect()
        stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        return {
            'stdout': stdout.read().decode('utf-8', errors='ignore'),
            'stderr': stderr.read().decode('utf-8', errors='ignore'),
            'exit_code': stdout.channel.recv_exit_status(),
        }
    def close(self):
        if self._client:
            self._client.close()

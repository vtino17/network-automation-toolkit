from abc import ABC, abstractmethod
class BaseDevice(ABC):
    def __init__(self, hostname, ip, port=22, username="admin", password=None):
        self.hostname = hostname
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self._connection = None
        self._facts = {}
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def disconnect(self):
        pass
    @abstractmethod
    def get_config(self):
        pass
    @abstractmethod
    def get_facts(self):
        pass
    @abstractmethod
    def execute(self, command):
        pass
    def ping(self, count=3):
        import subprocess
        import platform
        param = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(
            ["ping", param, str(count), self.ip],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.hostname} ({self.ip})>"

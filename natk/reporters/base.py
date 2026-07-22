from abc import ABC, abstractmethod
class BaseReporter(ABC):
    @abstractmethod
    def generate(self, data, output_path):
        pass

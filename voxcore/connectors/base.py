from abc import ABC, abstractmethod

class BaseConnector(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def get_schema(self) -> dict:
        pass

    @abstractmethod
    def execute_query(self, query: str):
        pass

from abc import ABC, abstractmethod

class BaseModel(ABC):
    
    def __init__(self, uri):
        self.uri = uri
    
    @abstractmethod
    def _connect(self):
        pass
    
    @abstractmethod
    def get_tables(self):
        pass
    
    @abstractmethod
    def read_table(self, table_name):
        pass
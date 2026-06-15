from abc import ABC, abstractmethod
import json


class BaseInsert(ABC):
    
    @abstractmethod
    def insert(self, data: json, table_name: str):
        pass
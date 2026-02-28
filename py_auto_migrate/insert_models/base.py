from abc import ABC, abstractmethod
import pandas as pd


class BaseInsert(ABC):
    
    @abstractmethod
    def insert(self, df: pd.DataFrame, table_name: str):
        pass
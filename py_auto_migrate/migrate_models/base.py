from abc import ABC, abstractmethod
from typing import Any


class BaseMigration(ABC):

    def __init__(self, source_uri: str, target_uri: str, inserter_class: Any):
        self.source_uri = source_uri
        self.target_uri = target_uri
        self.inserter = inserter_class(target_uri)
        self._initialize_source_connection()
    

    @abstractmethod
    def _initialize_source_connection(self):
        pass
    
    @abstractmethod
    def read_table(self, table_name: str) -> Any:
        pass
    
    @abstractmethod
    def get_tables(self) -> list:
        pass
    
    def migrate_one(self, table_name: str, ai_ask=None, ai_model=None ) -> None:

        data = self.read_table(table_name)

        if data and len(data) > 0:
            print(f"  📊 Migrating {table_name}")
            self.inserter.insert(data, table_name, ai_ask, ai_model)
            print(f"  ✅ Completed: {table_name}")
        else:
            print(f"  ⚠️ No data in {table_name}")
        
    def migrate_all(self) -> None:

        tables = self.get_tables()
        print(f"📋 Found {len(tables)} tables to migrate")
        
        for i, table in enumerate(tables, 1):
            print(f"\n➡ [{i}/{len(tables)}] Migrating: {table}")
            try:
                self.migrate_one(table)
            except Exception as e:
                print(f"  ❌ Error migrating {table}: {str(e)}")
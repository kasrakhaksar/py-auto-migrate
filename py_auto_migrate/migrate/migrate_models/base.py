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

    
    def get_foreignkey_dependencies(self, table_name: str) -> list[str]:
        return []
        

    def migrate_one(self, table_name: str, ai_ask=None, ai_model=None , dep=False) -> None:

        data = self.read_table(table_name)

        if data is not None and not data.empty:
            print(f"→ Migrating table: {table_name}")
            self.inserter.insert(data, table_name, ai_ask, ai_model)
            print(f"✅ Completed {table_name}")
        else:
            print(f"⚠️ No data in {table_name}")



        if dep == True :
            foreignkey_dependencies_tables = self.get_foreignkey_dependencies(table_name)
            
            for rel_table in foreignkey_dependencies_tables:
                print(f"→ Migrating dependent table: {rel_table}")

                rel_data = self.read_table(rel_table)

                if rel_data is not None and not rel_data.empty:
                    self.inserter.insert(rel_data, rel_table)

                print(f"✅ Completed {rel_table}")




    def migrate_all(self , ai_ask=None, ai_model=None , dep=False) -> None:

        tables = self.get_tables()

        for i, table_name in enumerate(tables, 1):
            print(f"\n➡ [{i}/{len(tables)}] Migrating: {table_name}")
            self.migrate_one(table_name , ai_ask , ai_model , dep)

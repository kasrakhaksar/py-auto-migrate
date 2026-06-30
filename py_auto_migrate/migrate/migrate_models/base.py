from abc import ABC, abstractmethod
from typing import Any
from py_auto_migrate.migrate.utils.type_mapper import normalize_datetime


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

        df = self.read_table(table_name)
        df = normalize_datetime(df)

        if df is not None and not df.empty:
            print(f"→ Migrating table: {table_name}")
            migrate_state = self.inserter.insert(df, table_name, ai_ask, ai_model)
            if migrate_state == True:
                print(f"✅ Completed {table_name}")
            else :
                print(f"❌ Error {table_name}")
        else:
            print(f"⚠️ No data in {table_name}")



        if dep == True :

            foreignkey_dependencies_tables = self.get_foreignkey_dependencies(table_name)
            
            for rel_table in foreignkey_dependencies_tables:

                rel_df = self.read_table(rel_table)
                rel_df = normalize_datetime(rel_df)

                
                if rel_df is not None and not rel_df.empty:
                    print(f"→ Migrating dependent table: {rel_table}")
                    migrate_state = self.inserter.insert(rel_df, rel_table)
                    if migrate_state == True:
                        print(f"✅ Completed {rel_table}")
                    else:
                        print(f"❌ Error {table_name}")
                else:
                    print(f"⚠️ No data in {table_name}")


    def migrate_all(self , ai_ask=None, ai_model=None , dep=False) -> None:

        tables = self.get_tables()

        for i, table_name in enumerate(tables, 1):
            print(f"\n➡ [{i}/{len(tables)}] Migrating: {table_name}")
            self.migrate_one(table_name , ai_ask , ai_model , dep)

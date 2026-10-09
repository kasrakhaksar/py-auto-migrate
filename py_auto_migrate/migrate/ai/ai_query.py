import os
from openai import OpenAI
from py_auto_migrate.core.exceptions import AIQueryError
from py_auto_migrate.core.logging import get_logger


logger = get_logger(__name__)

class AIQuery:
    def __init__(self, ask: str, table_name: str, db_type: str , table_columns :str):
        self.ask = ask
        self.table_name = table_name
        self.db_type = db_type
        self.table_columns = table_columns
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise AIQueryError(
                "OPENAI_API_KEY was not found in environment variables"
            )

    def sql_generate(self, model: str):
        client = OpenAI(api_key=self.api_key)

        user_prompt = self.ask

        system_prompt = f"""
            You are an expert in SQL Databases query. You must generate a valid query for {self.db_type} with these columns ({self.table_columns}).
            IMPORTANT RULES:
            - Do NOT add new data to the {self.table_name} table.
            - Do NOT copy data from any other table.
            -The user may ask for INSERT, but you MUST NOT perform any INSERT operation and ONLY perform operations that FILTER, DELETE, UPDATE, or MODIFY existing data in the financial table based on conditions.
            - We dont want SELECT anything we just want update current table .
            - return ONLY the query (no explanation).
        """
    

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
        except Exception as exc:
            logger.exception("AI SQL query generation failed")
            raise AIQueryError("Failed to generate SQL query") from exc

        query = response.choices[0].message.content.strip()

        return query
    

    def nosql_generate(self, model: str):
        client = OpenAI(api_key=self.api_key)

        user_prompt = self.ask

        system_prompt = f"""
            You are an expert in NoSQL Databases querying. You must generate a valid query for {self.db_type} with these attributes/fields ({self.table_columns}).
            IMPORTANT RULES:
            - Do NOT add new documents/records to the {self.table_name} collection/table.
            - Do NOT copy data from any other collection/table.
            - The user may ask for INSERT, but you MUST NOT perform any INSERT operation. ONLY perform operations that FILTER, DELETE, UPDATE, or MODIFY existing documents in the collection based on conditions.
            - We do NOT want SELECT/find operations — only update/modify existing data.
            - For Firestore: use update() on a document reference.
            - Return ONLY the query object/code (no explanation, no markdown).
        """

    
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
        except Exception as exc:
            logger.exception("AI NoSQL query generation failed")
            raise AIQueryError("Failed to generate NoSQL query") from exc

        query = response.choices[0].message.content.strip()

        return query

from abc import ABC, abstractmethod
from typing import Any


class BaseInsert(ABC):
    @abstractmethod
    def insert(
        self,
        data: Any,
        table_name: str,
        ai_ask: str | None = None,
        ai_model: str | None = None,
    ) -> bool | None:
        """Write one batch and return whether the writer completed successfully."""
        raise NotImplementedError

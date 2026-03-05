from abc import ABC, abstractmethod
from datetime import timezone
from typing import Any


class BaseDTO[M](ABC):

    @staticmethod
    @abstractmethod
    def from_entity_to_dict(model: M, excludes: list[str] = None) -> dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def from_dict_to_entity(data: dict[str, Any]) -> M:
        pass

    @staticmethod
    def _ensure_utc(dt):
        """Приводит naive datetime к UTC, если часовой пояс не указан"""
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

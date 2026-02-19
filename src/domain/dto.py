from abc import ABC, abstractmethod
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

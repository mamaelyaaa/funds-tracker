from typing import Any

from domain.dto import BaseDTO
from domain.users.entity import User
from domain.users.values import UserId


class UserDTO(BaseDTO):

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> User:
        user = User(
            id=UserId(data.get("id")),
            username=data.get("username"),
            password=data.get("password"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        # user.events.clear()
        return user

    @staticmethod
    def from_entity_to_dict(model: User, excludes: list[str] = None) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id,
            "username": model.username,
            "password": model.password,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data

from typing import Any

from domain.auth.entity import UserSession, UserSessionId
from domain.dto import BaseDTO
from domain.users.values import UserId


class UserSessionDTO(BaseDTO):

    @staticmethod
    def from_entity_to_dict(
        model: UserSession, excludes: list[str] = None
    ) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id,
            "user_id": model.user_id,
            "refresh_jti": model.refresh_jti,
            "expires_in": model.expires_in,
            "fingerprint": model.fingerprint,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> UserSession:
        account = UserSession(
            id=UserSessionId(data.get("id")),
            user_id=UserId(data.get("user_id")),
            refresh_jti=data.get("refresh_jti"),
            fingerprint=data.get("fingerprint"),
            expires_in=data.get("expires_in"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        return account

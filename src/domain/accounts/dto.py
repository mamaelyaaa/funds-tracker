from typing import Any

from domain.users.values import UserId
from .entity import Account
from .values import AccountId, Title


class AccountDTO:

    @staticmethod
    def from_entity_to_dict(
        entity: Account, excludes: list[str] = None
    ) -> dict[str, Any]:

        if not excludes:
            excludes = []

        data = {
            "id": entity.id.as_generic_type(),
            "user_id": entity.user_id.as_generic_type(),
            "name": entity.name.as_generic_type(),
            "type": entity.type,
            "currency": entity.currency,
            "balance": entity.balance,
            "created_at": entity.created_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> Account:
        return Account(
            id=AccountId(data.get("id")),
            user_id=UserId(data.get("user_id")),
            name=Title(data.get("name")),
            type=data.get("type"),
            currency=data.get("currency"),
            balance=data.get("balance"),
            created_at=data.get("created_at"),
        )

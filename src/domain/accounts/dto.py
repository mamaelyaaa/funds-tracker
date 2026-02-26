from typing import Any

from domain.dto import BaseDTO
from domain.users.values import UserId
from .entity import Account
from .values import AccountId, Title, Money


class AccountDTO(BaseDTO):

    @staticmethod
    def from_entity_to_dict(
        model: Account, excludes: list[str] = None
    ) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id.as_generic_type(),
            "user_id": model.user_id.as_generic_type(),
            "name": model.name.as_generic_type(),
            "type": model.type,
            "currency": model.currency,
            "balance": model.balance.as_generic_type(),
            "created_at": model.created_at,
            "updated_at": model.updated_at,
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
            balance=Money(data.get("balance")),
            type=data.get("type"),
            currency=data.get("currency"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

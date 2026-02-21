from typing import Any

from domain.accounts.values import AccountId, Money
from domain.dto import BaseDTO
from domain.histories.entities import History
from domain.histories.values import HistoryId


class HistoryDTO(BaseDTO):

    @staticmethod
    def from_entity_to_dict(
        entity: History, excludes: list[str] = None
    ) -> dict[str, Any]:

        if not excludes:
            excludes = []

        data = {
            "id": entity.id.as_generic_type(),
            "account_id": entity.account_id.as_generic_type(),
            "balance": entity.balance.as_generic_type(),
            "delta": entity.delta,
            "created_at": entity.created_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> History:
        return History(
            id=HistoryId(data.get("id")),
            account_id=AccountId(data.get("account_id")),
            balance=Money(data.get("balance")),
            created_at=data.get("created_at"),
            delta=float(Money.to_decimal(data.get("delta"))),
        )

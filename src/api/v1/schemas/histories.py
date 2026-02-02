from datetime import datetime

from pydantic import BaseModel

from domain.histories.domain import AccountHistory


class HistoryDetailSchema(BaseModel):
    # id: str
    balance: float
    created_at: datetime

    @classmethod
    def from_model(cls, history: AccountHistory) -> "HistoryDetailSchema":
        return HistoryDetailSchema(
            # id=history.id.value,
            balance=history.balance,
            created_at=history.created_at,
        )

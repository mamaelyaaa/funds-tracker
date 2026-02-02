from pydantic import BaseModel


class NetWorthBalanceSchema(BaseModel):
    total_balance: float

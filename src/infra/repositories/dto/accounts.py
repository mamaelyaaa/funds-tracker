from domain.accounts.dto import AccountDTO
from domain.accounts.entity import Account
from domain.accounts.values import AccountId
from domain.users.values import UserId
from domain.values import Title, Money
from infra.models import AccountModel
from infra.repositories.dto.base import BaseOrmDTO


class AccountOrmDTO(BaseOrmDTO, AccountDTO):

    @staticmethod
    def from_orm_to_entity(model: AccountModel) -> Account:
        return Account(
            id=AccountId(model.id),
            user_id=UserId(model.user_id),
            name=Title(model.name),
            type=model.type,
            currency=model.currency,
            balance=Money(model.balance),
            created_at=AccountOrmDTO._ensure_utc(model.created_at),
            updated_at=AccountOrmDTO._ensure_utc(model.updated_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: Account) -> AccountModel:
        return AccountModel(**AccountDTO.from_entity_to_dict(entity))

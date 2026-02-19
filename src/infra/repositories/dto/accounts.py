from domain.accounts.dto import AccountDTO
from domain.accounts.entity import Account
from domain.accounts.values import AccountId, Title
from domain.users.values import UserId
from infra.models import AccountModel


class AccountOrmDTO(AccountDTO):

    @staticmethod
    def from_orm_to_entity(model: AccountModel) -> Account:
        return Account(
            id=AccountId(model.id),
            user_id=UserId(model.user_id),
            name=Title(model.name),
            type=model.type,
            currency=model.currency,
            balance=model.balance,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: Account) -> AccountModel:
        return AccountModel(**AccountDTO.from_entity_to_dict(entity))

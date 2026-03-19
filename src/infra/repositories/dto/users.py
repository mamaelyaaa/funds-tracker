from domain.users.dto import UserDTO
from domain.users.entity import User
from domain.users.values import UserId
from infra.models import UserModel
from infra.repositories.dto.base import BaseOrmDTO


class UserOrmDTO(BaseOrmDTO, UserDTO):

    @staticmethod
    def from_orm_to_entity(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            name=model.name,
            created_at=UserDTO.ensure_utc(model.created_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: User) -> UserModel:
        return UserModel(**UserDTO.from_entity_to_dict(entity))

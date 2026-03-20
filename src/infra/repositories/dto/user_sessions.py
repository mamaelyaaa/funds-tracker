from domain.auth.dto import UserSessionDTO
from domain.auth.entity import UserSession, UserSessionId
from domain.users.dto import UserDTO
from domain.users.values import UserId
from infra.models import UserSessionModel
from infra.repositories.dto.base import BaseOrmDTO


class UserSessionOrmDTO(BaseOrmDTO, UserSessionDTO):

    @staticmethod
    def from_orm_to_entity(model: UserSessionModel) -> UserSession:
        return UserSession(
            id=UserSessionId(model.id),
            user_id=UserId(model.user_id),
            refresh_jti=model.refresh_jti,
            fingerprint=model.fingerprint,
            expires_in=UserSessionDTO.ensure_utc(model.expires_in),
            created_at=UserDTO.ensure_utc(model.created_at),
            updated_at=UserDTO.ensure_utc(model.updated_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: UserSession) -> UserSessionModel:
        return UserSessionModel(**UserSessionDTO.from_entity_to_dict(entity))

from datetime import datetime

from authx import TokenPayload
from black import timezone
from fastapi.responses import Response

from domain.auth.entity import UserSession
from domain.auth.protocols import UserSessionRepositoryProtocol
from domain.users.values import UserId
from infra.auth.authx import auth
from infra.database.specification import OrderBySpecification
from infra.repositories.dto.user_sessions import UserSessionOrmDTO


class TokenService:

    def __init__(self, user_session_repo: UserSessionRepositoryProtocol):
        self.user_session_repo = user_session_repo

    @staticmethod
    def create_access_token(uid: str, *args, **kwargs) -> str:
        """Создает токен доступа"""
        return auth.create_access_token(uid=uid, **kwargs)

    @staticmethod
    def create_refresh_token(uid: str, *args, **kwargs) -> str:
        """Создает токен обновления"""
        return auth.create_refresh_token(uid=uid, **kwargs)

    async def save_or_update_refresh(self, refresh: str) -> None:
        token: TokenPayload = auth.verify_token(token=refresh)

        # Если пользователь уже имеет активную сессию, то она просто обновляется
        # Если у пользователя нет активной сессии, создается новая и старые удаляются

        sessions = await self.user_session_repo.find_all(
            OrderBySpecification(field="expires_in", direction="desc"),
            user_id=token.sub,
        )
        session_ids_for_delete: list[str] = [session.id for session in sessions]

        for session in sessions:
            new_user_session = UserSession(
                user_id=UserId(token.sub),
                refresh_jti=token.jti,
                expires_in=token.exp,
            )

            # Если в БД есть запись с валидной записью - обновляем
            if session.expires_in >= datetime.now(timezone.utc):
                await self.user_session_repo.update(
                    upd_data=UserSessionOrmDTO.from_entity_to_dict(new_user_session),
                    user_id=token.sub,
                    id=session.id,
                    commit=False,
                )
                session_ids_for_delete.pop()
                break

            # Если такой записи нет - создаем новую
            else:
                await self.user_session_repo.save(new_user_session, commit=False)
                break

        await self.user_session_repo.delete_many(
            sessions_ids=session_ids_for_delete,
            commit=True,
        )

        return token.jti

    @staticmethod
    def save_refresh_token_cookie(refresh_jti: str, response: Response) -> None:
        # Сохраняем в куки
        auth.set_refresh_cookies(token=refresh_jti, response=response)
        return

from datetime import datetime

import structlog
from authx import TokenPayload
from black import timezone
from fastapi.responses import Response

from core.settings import settings
from domain.auth.entity import UserSession
from domain.auth.protocols import UserSessionRepositoryProtocol
from domain.users.values import UserId
from infra.auth.authx import auth
from infra.auth.exceptions import RefreshNotFoundException
from infra.database.specification import OrderBySpecification, DateRangeSpecification
from infra.models import UserSessionModel
from infra.repositories.dto.user_sessions import UserSessionOrmDTO

logger = structlog.get_logger()


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

    async def save_or_update_refresh(self, refresh: str, fingerprint: str) -> None:
        token = TokenPayload.decode(
            token=refresh, key=settings.jwt.secret, verify=False
        )

        # Если пользователь уже имеет активную сессию, то она просто обновляется
        # Если у пользователя нет активной сессии, создается новая и старые удаляются

        exists_sessions = await self.user_session_repo.find_all(
            OrderBySpecification(field="updated_at", direction="asc"),
            user_id=token.sub,
        )

        if len(exists_sessions) >= UserSession.MAX_AUTHORIZED:
            logger.warning(
                "Превышен лимит входов в систему. Деактивируем самый первый вход",
                fingerprint=exists_sessions[0].fingerprint,
            )
            await self.user_session_repo.delete_one(
                user_id=token.sub, id=exists_sessions[0].id, commit=False
            )

        exists_session = await self.user_session_repo.find_one(
            DateRangeSpecification(
                model=UserSessionModel,
                field="expires_in",
                start=datetime.now(timezone.utc),
            ),
            user_id=token.sub,
            fingerprint=fingerprint,
        )

        if exists_session:
            exists_session.expires_in = token.exp
            exists_session.refresh_jti = token.jti
            exists_session.touch()

            await self.user_session_repo.update(
                upd_data=UserSessionOrmDTO.from_entity_to_dict(
                    exists_session, excludes=["id", "user_id", "fingerprint"]
                ),
                user_id=token.sub,
                id=exists_session.id,
                commit=True,
            )
        else:

            await self.user_session_repo.delete_expired_by_user(
                user_id=token.sub,
                expired_before=datetime.now(timezone.utc),
                commit=False,
            )

            new_user_session = UserSession(
                user_id=UserId(token.sub),
                refresh_jti=token.jti,
                expires_in=token.exp,
                fingerprint=fingerprint,
            )

            await self.user_session_repo.save(new_user_session, commit=True)

        return

    @staticmethod
    def get_refresh_jti(refresh: str) -> str:
        token = TokenPayload.decode(
            token=refresh, key=settings.jwt.secret, verify=False
        )
        return token.jti

    @staticmethod
    def save_refresh_token_cookie(refresh_jti: str, response: Response) -> None:
        # Сохраняем в куки
        response.set_cookie(
            key=settings.jwt.refresh_cookie_name,
            value=refresh_jti,
            path=settings.jwt.refresh_cookie_path,
            domain=settings.jwt.cookie_domain,
            secure=settings.jwt.cookie_secure,
            httponly=settings.jwt.cookie_http_only,
            max_age=int(settings.jwt.cookie_max_age),
        )
        return

    @staticmethod
    def delete_refresh_token_cookie(response: Response) -> None:
        response.delete_cookie(
            key=settings.jwt.refresh_cookie_name,
            path=settings.jwt.refresh_cookie_path,
            domain=settings.jwt.cookie_domain,
            secure=settings.jwt.cookie_secure,
            httponly=settings.jwt.cookie_http_only,
        )
        return

    async def get_refresh_by_jti(self, refresh_jti: str) -> UserSession:
        user_session = await self.user_session_repo.find_one(refresh_jti=refresh_jti)
        if not user_session:
            logger.warning("Токен обновления не найден в Cookie")
            raise RefreshNotFoundException
        return user_session

    async def get_refresh_token_by_fingerprint(
        self, user_id: str, fingerprint: str
    ) -> UserSession:
        user_session = await self.user_session_repo.find_one(
            user_id=user_id, fingerprint=fingerprint
        )
        if not user_session:
            logger.warning("Токен обновления не найден в системе")
            raise RefreshNotFoundException
        return user_session

    async def delete_refresh_token(self, user_id: str, fingerprint: str) -> None:
        await self.get_refresh_token_by_fingerprint(
            user_id=user_id, fingerprint=fingerprint
        )
        await self.user_session_repo.delete_one(
            user_id=user_id, fingerprint=fingerprint
        )
        return

    async def delete_all_user_refresh_tokens(self, user_id: str) -> None:
        await self.user_session_repo.delete_all(user_id=user_id)
        return

from authx import AuthXConfig, AuthX

from core.config import settings

config = AuthXConfig(
    JWT_ALGORITHM=settings.jwt.algorithm,
    JWT_SECRET_KEY=settings.jwt.secret,
    JWT_SESSION_COOKIE=settings.jwt.cookie_session,
    JWT_COOKIE_SECURE=settings.jwt.cookie_secure,
    JWT_COOKIE_HTTP_ONLY=settings.jwt.cookie_http_only,
    JWT_REFRESH_COOKIE_NAME=settings.jwt.refresh_cookie_name,
    JWT_REFRESH_COOKIE_PATH=settings.jwt.refresh_cookie_path,
    JWT_COOKIE_MAX_AGE=settings.jwt.cookie_max_age,
    JWT_COOKIE_DOMAIN=settings.jwt.cookie_domain,
)

auth = AuthX(config=config)

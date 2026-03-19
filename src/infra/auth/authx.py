from authx import AuthXConfig, AuthX

from core.settings import settings

config = AuthXConfig(
    JWT_ALGORITHM=settings.jwt.algorithm,
    JWT_SECRET_KEY=settings.jwt.secret,
)

auth = AuthX(config=config)

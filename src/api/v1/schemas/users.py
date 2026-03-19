import uuid
from datetime import datetime

from pydantic import SecretStr

from api.schemas import BaseApiModel


class RegisterUserSchema(BaseApiModel):
    username: str
    password: SecretStr
    password_repeat: SecretStr


class LoginUserSchema(BaseApiModel):
    username: str
    password: SecretStr


class BearerTokenSchema(BaseApiModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserDetailSchema(BaseApiModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    updated_at: datetime

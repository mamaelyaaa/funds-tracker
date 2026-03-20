import uuid
from datetime import datetime

from pydantic import SecretStr

from api.schemas import BaseApiModel


class RegisterUserSchema(BaseApiModel):
    username: str
    password: SecretStr
    password_repeat: SecretStr
    fingerprint: str


class TokenTypeMeta(BaseApiModel):
    token_type: str = "Bearer"


class LoginUserSchema(BaseApiModel):
    username: str
    password: SecretStr
    fingerprint: str


class UserDetailSchema(BaseApiModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    updated_at: datetime

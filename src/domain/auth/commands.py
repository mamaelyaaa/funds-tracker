from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    username: str
    password: str
    password_repeat: str


@dataclass(frozen=True)
class LoginUserCommand:
    username: str
    password: str

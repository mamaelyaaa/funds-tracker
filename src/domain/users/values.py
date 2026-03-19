from core.domain import DomainId
from domain.users.exceptions import TooLargeUsernameException


class UserId(DomainId):
    """Value-obj уникального id пользователя"""

    pass


class Username(str):
    MAX_LEN: int = 31

    def __new__(cls, value: str):
        if len(value) > cls.MAX_LEN:
            raise TooLargeUsernameException

        return super().__new__(cls, value)

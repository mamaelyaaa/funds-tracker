from infra.auth.authx import auth


class TokenService:

    # def __init__(self, user_sessions_repo):
    #     self.user_sessions_repo = user_sessions_repo

    @staticmethod
    def create_access_token(uid: str, scope: list[str], *args, **kwargs) -> str:
        return auth.create_access_token(uid=uid, scope=scope, **kwargs)

    def create_refresh_token(self, uid: str, *args, **kwargs) -> str:
        raise NotImplementedError

    def save_refresh_token(self, refresh: str) -> None:
        raise NotImplementedError

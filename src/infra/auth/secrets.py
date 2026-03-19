import bcrypt


class BcryptService:

    @staticmethod
    def hash(password: str) -> str:
        pwd = bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt())
        return pwd.decode()

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

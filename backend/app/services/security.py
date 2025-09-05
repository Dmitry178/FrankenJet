import jwt

from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from app.core.config_env import settings


class SecurityService:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    @staticmethod
    def create_jwt_token(payload_data: dict, expire: int) -> str:
        """
        Создание JWT-токена

        :param payload_data: данные для упаковки в тело токена
        :param expire: время жизни токена
        """

        iat = datetime.now(timezone.utc)
        expire_date = iat + timedelta(minutes=expire)
        payload = {**payload_data, "iat": iat, "exp": expire_date}
        encoded_jwt = jwt.encode(payload=payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Извлечение данных из JWT токена
        """

        try:
            payload = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
            return payload

        except:  # noqa
            # TODO: сделать обработку исключений
            return {}

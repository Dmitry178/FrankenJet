import bcrypt
import jwt

from datetime import datetime, timezone, timedelta

from app.config.app import JWT_ALGORITHM
from app.config.env import settings
from app.core.logs import logger


class SecurityService:

    @staticmethod
    def hash_password(password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        pwd_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)

    @staticmethod
    def create_jwt_token(payload_data: dict, expire: int | datetime) -> str:
        """
        Создание JWT-токена

        :param payload_data: данные для упаковки в тело токена
        :param expire: время жизни токена
        """

        iat = datetime.now(timezone.utc)

        if isinstance(expire, int):
            expire_date = iat + timedelta(minutes=expire)
        elif isinstance(expire, datetime):
            expire_date = expire
        else:
            raise TypeError("Ошибка типа expire")

        payload = {**payload_data, "iat": iat, "exp": expire_date}
        encoded_jwt = jwt.encode(payload=payload, key=settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Извлечение данных из JWT токена
        """

        try:
            payload = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
            return payload

        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError, jwt.InvalidTokenError) as ex:
            logger.warning(ex)
            return {}

        except Exception as ex:
            logger.exception(ex)
            return {}

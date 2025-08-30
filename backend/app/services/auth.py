import jwt

from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from app.core.config import settings
from app.db.db_manager import DBManager
from app.exceptions import EUserNotFound, EPasswordIncorrect
from app.schemas.auth import SUserLogin


class AuthTokenService:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    @staticmethod
    def create_access_token(payload_data: dict) -> str:
        """
        Создание JWT access-токена

        :param payload_data: данные для упаковки в тело токена
        """

        expire_date = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload = {**payload_data, "exp": expire_date}
        encoded_jwt = jwt.encode(payload=payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return encoded_jwt

    # TODO: сделать создание refresh-токена и обновление access-токена

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


class AuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def login(self, data: SUserLogin) -> str:
        """
        Проверка пользователя и пароля, выпуск access-токена
        """

        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise EUserNotFound

        if not AuthTokenService().verify_password(data.password, user.hashed_password):
            raise EPasswordIncorrect

        payload_data = {"id": user.id}
        access_token = AuthTokenService().create_access_token(payload_data)

        return access_token

import jwt

from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from app.core.config import settings
from app.core.config_const import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from app.db.db_manager import DBManager
from app.exceptions import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx
from app.schemas.auth import SLoginUser, SRegisterUser, SAuthTokens, SUserInfo


class AuthTokenService:

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


class AuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def login(self, data: SLoginUser) -> SAuthTokens:
        """
        Проверка пользователя и пароля, выпуск access и refresh токенов
        """

        # TODO: добавить роли пользователя в базу и получение ролей пользователя
        user = await self.db.users.select_one_or_none(email=data.email)
        if not user:
            raise UserNotFoundEx

        if not AuthTokenService().verify_password(data.password, user.hashed_password):
            raise PasswordIncorrectEx

        # TODO: добавить роли в access_token
        access_token = AuthTokenService().create_jwt_token(
            {"id": user.id, "type": TOKEN_TYPE_ACCESS, "email": data.email},
            settings.JWT_ACCESS_EXPIRE_MINUTES
        )
        refresh_token = AuthTokenService().create_jwt_token(
            {"id": user.id, "type": TOKEN_TYPE_REFRESH},
            settings.JWT_REFRESH_EXPIRE_MINUTES
        )

        return SAuthTokens(access_token=access_token, refresh_token=refresh_token)

    async def register_user(self, data: SLoginUser) -> None:
        """
        Регистрация пользователя
        """

        hashed_password = AuthTokenService().hash_password(data.password)
        new_user_data = SRegisterUser(email=data.email, hashed_password=hashed_password)

        # TODO: добавить отправку и валидацию кода подтверждения на email
        # TODO: добавить try/except

        if await self.db.users.is_exists(email=data.email):
            raise UserExistsEx()

        await self.db.users.insert_model_data(new_user_data)
        await self.db.commit()

        return None

    async def get_user_info(self, user_id: int) -> SUserInfo:
        """
        Получение информации о пользователе по его id
        """

        user = await self.db.users.select_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundEx

        return SUserInfo.model_validate(user)

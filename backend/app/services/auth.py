from uuid import uuid4

from app.core.config import settings
from app.core.config_const import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from app.db.db_manager import DBManager
from app.exceptions import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx, TokenTypeErrorEx, TokenInvalidEx
from app.schemas.auth import SLoginUser, SRegisterUser, SAuthTokens, SUserInfo
from app.services.security import SecurityService


class AuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @staticmethod
    async def issue_tokens(user_id: int, email: str, roles: list | None) -> SAuthTokens:
        """
        Выпуск токенов
        """

        access_token = SecurityService().create_jwt_token(
            {"id": user_id, "type": TOKEN_TYPE_ACCESS, "email": email, "roles": roles},
            settings.JWT_ACCESS_EXPIRE_MINUTES
        )

        # TODO: сделать хранение токена (или jti) в базе
        refresh_token = SecurityService().create_jwt_token(
            {"id": user_id, "type": TOKEN_TYPE_REFRESH, "jti": str(uuid4())},
            settings.JWT_REFRESH_EXPIRE_MINUTES
        )

        return SAuthTokens(access_token=access_token, refresh_token=refresh_token)

    async def login(self, data: SLoginUser) -> SAuthTokens:
        """
        Проверка пользователя и пароля, выпуск access и refresh токенов
        """

        user = await self.db.users.get_user_with_roles(email=data.email)
        if not user:
            raise UserNotFoundEx

        roles = [role.role for role in user.roles]  # список ролей пользователя

        if not SecurityService().verify_password(data.password, user.hashed_password):
            raise PasswordIncorrectEx

        return await self.issue_tokens(user.id, user.email, roles)

    async def refresh(self, refresh_token: str) -> SAuthTokens:
        """
        Перевыпуск access и refresh токенов
        """

        # TODO: сделать отзыв токена в базе

        refresh_token_payload = SecurityService().decode_token(refresh_token)
        if not refresh_token_payload:
            raise TokenInvalidEx

        if refresh_token_payload.get("type") != TOKEN_TYPE_REFRESH:
            raise TokenTypeErrorEx

        user_id = refresh_token_payload.get("id")

        user = await self.db.users.get_user_with_roles(id=user_id)
        if not user:
            raise UserNotFoundEx

        roles = [role.role for role in user.roles]

        return await self.issue_tokens(user_id, user.email, roles)

    async def register_user(self, data: SLoginUser) -> None:
        """
        Регистрация пользователя
        """

        hashed_password = SecurityService().hash_password(data.password)
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

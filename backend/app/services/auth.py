from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import uuid4, UUID

from app.core.config_env import settings
from app.core.config_app import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from app.core.logs import logger
from app.db.db_manager import DBManager
from app.exceptions.auth import UserNotFoundEx, PasswordIncorrectEx, TokenTypeErrorEx, TokenInvalidEx
from app.schemas.auth import SLoginUser, SAuthTokens
from app.services.security import SecurityService


class AuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def issue_tokens(self, user_id: int, email: str, roles: list | None, jti: UUID | None = None) -> SAuthTokens:
        """
        Выпуск токенов
        """

        access_token = SecurityService().create_jwt_token(
            {"id": user_id, "type": TOKEN_TYPE_ACCESS, "email": email, "roles": roles},
            settings.JWT_ACCESS_EXPIRE_MINUTES
        )

        new_jti = uuid4()
        refresh_token = SecurityService().create_jwt_token(
            {"id": user_id, "type": TOKEN_TYPE_REFRESH, "jti": str(new_jti)},
            settings.JWT_REFRESH_EXPIRE_MINUTES
        )

        # регистрация токена
        await self.register_user_jti(user_id, new_jti)

        # отзыв токена
        if jti:
            await self.revoke_user_jti(user_id, jti)

        return SAuthTokens(access_token=access_token, refresh_token=refresh_token)

    async def prepare_user_data(self, user, tokens=True, jti: UUID | None = None) -> dict:
        """
        Подготовка словаря с данными пользователя
        """

        roles = [role.role for role in user.roles]  # список ролей пользователя
        user_data = {
            "tokens": (await self.issue_tokens(user.id, user.email, roles, jti)).model_dump()
        } if tokens else {}

        user_data |= {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "picture": user.picture,
            },
            "roles": roles,
        }

        return user_data

    async def login(self, data: SLoginUser) -> dict:
        """
        Проверка пользователя и пароля, выпуск access и refresh токенов
        """

        user = await self.db.users.get_user_with_roles(email=data.email)
        if not user:
            raise UserNotFoundEx

        if not SecurityService().verify_password(data.password, user.hashed_password):
            raise PasswordIncorrectEx

        return await self.prepare_user_data(user)

    async def refresh(self, refresh_token: str) -> dict:
        """
        Перевыпуск access и refresh токенов
        """

        refresh_token_payload = SecurityService().decode_token(refresh_token)
        if not refresh_token_payload:
            raise TokenInvalidEx

        if refresh_token_payload.get("type") != TOKEN_TYPE_REFRESH:
            raise TokenTypeErrorEx

        user_id = refresh_token_payload.get("id")
        jti = refresh_token_payload.get("jti")

        user = await self.db.users.get_user_with_roles(id=user_id)
        if not user:
            raise UserNotFoundEx

        return await self.prepare_user_data(user, jti=jti)

    async def get_user_info(self, user_id: int) -> dict:
        """
        Получение информации о пользователе по его id
        """

        user = await self.db.users.get_user_with_roles(id=user_id)
        if not user:
            raise UserNotFoundEx

        return await self.prepare_user_data(user, tokens=False)

    async def register_user_jti(self, user_id: int, jti: UUID) -> bool:
        """
        Регистрация refresh-токена (jti) в базе
        """

        try:
            await self.db.refresh_tokens.insert_data(
                user_id=user_id, jti=jti
            )
            await self.db.commit()
            return True

        except (IntegrityError, SQLAlchemyError, Exception) as ex:
            logger.error(ex)
            await self.db.rollback()
            return False

    async def revoke_user_jti(self, user_id: int, jti: UUID) -> bool:
        """
        Отзыв refresh-токена (jti) из базы
        """

        try:
            await self.db.refresh_tokens.delete(
                user_id=user_id, jti=jti
            )
            await self.db.commit()
            return True

        except (IntegrityError, SQLAlchemyError, Exception) as ex:
            logger.error(ex)
            await self.db.rollback()
            return False

from fastapi import Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import uuid4, UUID

from app.config.app import JWT_TYPE_ACCESS, JWT_TYPE_REFRESH, JWT_ACCESS_EXPIRE_MINUTES, JWT_REFRESH_EXPIRE_MINUTES, \
    JWT_ACCESS_LOCAL_EXPIRE_MINUTES
from app.config.env import settings, AppMode
from app.core import RMQManager
from app.core.db_manager import DBManager
from app.core.logs import logger
from app.exceptions.auth import UserNotFoundEx, PasswordIncorrectEx, TokenTypeErrorEx, TokenInvalidEx, UserNotActiveEx
from app.schemas.auth import SLoginUser, SAuthTokens
from app.services.bot import BotServices, MsgTypes
from app.services.security import SecurityService
from app.services.user_info import UserInfoServices


class AuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None, rmq: RMQManager | None = None) -> None:
        self.db = db
        self.rmq = rmq

    async def issue_tokens(
            self,
            user_id: UUID,
            email: str,
            roles: list | None,
            user_name: str | None = None,
            jti: UUID | None = None
    ) -> SAuthTokens:
        """
        Выпуск токенов
        """

        access_payload = {
            "id": str(user_id), "type": JWT_TYPE_ACCESS, "name": user_name, "email": email, "roles": roles
        }
        jwt_access_expire = JWT_ACCESS_LOCAL_EXPIRE_MINUTES \
            if settings.APP_MODE == AppMode.local else JWT_ACCESS_EXPIRE_MINUTES  # в локальном режиме своё значение
        access_token = SecurityService().create_jwt_token(access_payload, jwt_access_expire)

        new_jti = uuid4()
        refresh_payload = {"id": str(user_id), "type": JWT_TYPE_REFRESH, "jti": str(new_jti)}
        refresh_token = SecurityService().create_jwt_token(refresh_payload, JWT_REFRESH_EXPIRE_MINUTES)

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

        picture = settings.S3_DIRECT_URL + user.picture if user.picture else None

        user_data |= {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "picture": picture,
            },
            "roles": roles,
        }

        return user_data

    async def login(self, data: SLoginUser, request: Request) -> dict:
        """
        Проверка пользователя и пароля, выпуск access и refresh токенов
        """

        user = await self.db.users.get_user_with_roles(email=data.email)
        if not user:
            raise UserNotFoundEx

        if not user.is_active:
            raise UserNotActiveEx

        if not SecurityService().verify_password(data.password, user.hashed_password):
            raise PasswordIncorrectEx

        user_data = await self.prepare_user_data(user)
        if self.rmq and "admin" in user_data.get("roles", []):
            bot_notification = UserInfoServices().notification_message(user.id, data.email, request)
            await BotServices(self.rmq).send_message(MsgTypes.auth_notification, bot_notification)

        return user_data

    async def refresh(self, refresh_token: str) -> dict:
        """
        Перевыпуск access и refresh токенов
        """

        refresh_token_payload = SecurityService().decode_token(refresh_token)
        if not refresh_token_payload:
            raise TokenInvalidEx

        if refresh_token_payload.get("type") != JWT_TYPE_REFRESH:
            raise TokenTypeErrorEx

        user_id = refresh_token_payload.get("id")
        jti = refresh_token_payload.get("jti")

        # проверка пользователя и jti-токена
        user = await self.db.users.get_user_with_roles(id=user_id, is_active=True, jti=jti)
        if not user:
            raise UserNotFoundEx

        return await self.prepare_user_data(user, jti=jti)

    async def get_user_info(self, user_id: int) -> dict:
        """
        Получение информации о пользователе по его id
        """

        user = await self.db.users.get_user_with_roles(id=user_id, is_active=True)
        if not user:
            raise UserNotFoundEx

        return await self.prepare_user_data(user, tokens=False)

    async def register_user_jti(self, user_id: UUID, jti: UUID) -> bool:
        """
        Регистрация refresh-токена (jti) в базе
        """

        try:
            await self.db.auth.refresh_tokens.insert_one(
                user_id=user_id, jti=jti
            )
            await self.db.commit()
            return True

        except (IntegrityError, SQLAlchemyError, Exception) as ex:
            logger.exception(ex)
            await self.db.rollback()
            return False

    async def revoke_user_jti(self, user_id: UUID, jti: UUID | None = None) -> bool:
        """
        Отзыв refresh-токена (jti) / всех токенов из базы
        """

        try:
            kwargs = {"user_id": user_id}
            if jti:
                kwargs["jti"] = jti
            await self.db.auth.refresh_tokens.delete(commit=True, **kwargs)

            return True

        except (IntegrityError, SQLAlchemyError, Exception) as ex:
            logger.exception(ex)
            await self.db.rollback()
            return False

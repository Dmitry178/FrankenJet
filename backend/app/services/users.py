from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID

from app.config.app import BUCKET_IMAGES
from app.config.env import settings
from app.core.db_manager import DBManager
from app.core.logs import logger
from app.core.s3_manager import S3Manager
from app.db.models import Users
from app.decorators.db_errors import handle_basic_db_errors
from app.exceptions.auth import UserExistsEx, UserCreationErrorEx, UserNotFoundEx
from app.schemas.auth import SLoginUser, SRegisterUser
from app.schemas.users import SUserCreateOAuth2, SUserProfile, SEditUserProfile
from app.services.security import SecurityService


class UsersServices:

    db: DBManager | None
    s3: S3Manager | None

    def __init__(self, db: DBManager | None = None, s3: DBManager | None = None) -> None:
        self.db = db
        self.s3 = s3

    async def create_user_by_email(self, user_data: SLoginUser) -> UUID:
        """
        Создание пользователя (внутренняя регистрация по email)
        """

        try:
            hashed_password = SecurityService().hash_password(user_data.password)
            new_user_data = SRegisterUser(email=user_data.email, hashed_password=hashed_password)

            user = await self.db.users.insert_one(new_user_data, scalars=True)
            await self.db.commit()

            return user.id

        except IntegrityError as ex:
            # TODO: сделать дополнительную проверку на UniqueViolationError
            # пользователь уже существует, ошибка
            raise UserExistsEx from ex

        except SQLAlchemyError as ex:
            # ошибка базы данных
            logger.error(ex)
            raise UserCreationErrorEx from ex

        except Exception as ex:
            logger.exception(ex)
            raise UserCreationErrorEx from ex

    async def add_user_roles(self, user_id: UUID, roles: list) -> bool:
        """
        Назначение ролей пользователю
        """

        if not user_id:
            return False

        if not roles:
            return True

        user_roles = [{"user_id": user_id, "role_id": role} for role in roles]

        try:
            await self.db.auth.user_roles.insert_all(values=user_roles)
            await self.db.commit()
            return True

        except (IntegrityError, Exception) as ex:
            logger.exception(ex)
            return False

    async def get_or_create_user_by_oauth2(self, user_data: SUserCreateOAuth2):
        """
        Создание пользователя (при oauth2-аутентификации), получение id пользователя
        """

        try:
            user = await self.db.users.get_or_create_user(user_data)
            await self.db.commit()
            return user

        except SQLAlchemyError as ex:
            # ошибка базы данных
            await self.db.rollback()
            logger.error(ex)
            raise UserCreationErrorEx from ex

        except Exception as ex:
            await self.db.rollback()
            logger.exception(ex)
            raise UserCreationErrorEx from ex

    @staticmethod
    def _processing_user_dict(user: Users, add_roles=True) -> dict:
        """
        Обработка данных пользователя
        """

        user_dict = {
            k: v for k, v in vars(user).items()
            if not k.startswith("_") and k != "roles"
        }
        profile = SUserProfile.model_validate(user_dict)

        if add_roles:
            roles_list = [role.role for role in user.roles] if user.roles else []
            profile.roles = roles_list

        return profile.model_dump()

    @handle_basic_db_errors
    async def get_user_profile(self, user_id: UUID) -> dict:
        """
        Получение информации о профиле пользователя
        """

        user = await self.db.users.get_user_with_roles(id=user_id)
        if not user:
            raise UserNotFoundEx

        result = self._processing_user_dict(user)

        picture = result.get("picture")
        if picture:
            result["picture"] = settings.S3_DIRECT_URL + picture

        return result

    @handle_basic_db_errors
    async def get_paginated_users(self, page: int | None = None, page_size: int | None = None) -> list:
        """
        Получение списка пользователей с пагинацией
        """

        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            limit = page_size
        else:
            # случай, если какое-то из этих значений равно None
            offset = 0
            limit = 20

        users = await self.db.users.get_user_with_roles(offset=offset, limit=limit)

        return [self._processing_user_dict(user) for user in users]

    @handle_basic_db_errors
    async def edit_user_profile(self, user_id: UUID, data: SEditUserProfile) -> dict:
        """
        Обновление данных профиля пользователя
        """

        user = await self.db.users.update(data, id=user_id, scalars=True, commit=True)
        if not user:
            raise UserNotFoundEx()

        # await self.db.session.refresh(user, attribute_names=["roles"])

        result = self._processing_user_dict(user, add_roles=False)
        return result

    @handle_basic_db_errors
    async def load_avatar(self, user_id: UUID, content: bytes, content_type: str) -> dict | None:
        """
        Загрузка аватара пользователя
        """

        s3_key = f"/users/{user_id}/avatar.png"
        result = await self.s3.upload_from_memory(
                bucket=BUCKET_IMAGES, s3_key=s3_key, data=content, content_type=content_type
        )

        if not result:
            return None

        picture = f"/{BUCKET_IMAGES}{s3_key}"
        await self.db.users.update(data={"picture": picture}, id=user_id, commit=True)

        return {"picture": settings.S3_DIRECT_URL + picture}

    @handle_basic_db_errors
    async def delete_avatar(self, user_id: UUID):
        """
        Удаление аватара пользователя
        """

        # TODO: сделать удаление аватара из S3
        await self.db.users.update(data={"picture": None}, id=user_id, commit=True)

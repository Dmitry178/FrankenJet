from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.db_manager import DBManager
from app.core.logs import logger
from app.exceptions.auth import UserExistsEx, UserCreationErrorEx
from app.schemas.auth import SLoginUser, SRegisterUser
from app.schemas.users import SUserCreateOAuth2
from app.services.security import SecurityService


class UsersServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def create_user_by_email(self, user_data: SLoginUser) -> int:
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

    async def add_user_roles(self, user_id: int, roles: list) -> bool:
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

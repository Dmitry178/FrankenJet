from asyncpg import UniqueViolationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.logs import logger
from app.db.db_manager import DBManager
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

            user = await self.db.users.insert_one(new_user_data, scalar=True)
            await self.db.commit()

            return user.id

        except UniqueViolationError as ex:
            # пользователь уже существует, ошибка
            raise UserExistsEx from ex

        except (SQLAlchemyError, Exception) as ex:
            # ошибка базы данных
            logger.error(ex)
            raise UserCreationErrorEx from ex

    async def get_or_create_user_by_oauth2(self, user_data: SUserCreateOAuth2):
        """
        Создание пользователя (при oauth2-аутентификации), получение id пользователя
        """

        try:
            user = await self.db.users.get_or_create_user(user_data)
            await self.db.commit()
            return user

        except (SQLAlchemyError, Exception) as ex:
            # ошибка базы данных
            await self.db.rollback()
            logger.error(ex)
            raise UserCreationErrorEx from ex

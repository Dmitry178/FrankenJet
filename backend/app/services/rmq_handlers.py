""" Обработчик сообщений от бота уведомлений через RabbitMQ """

from uuid import UUID

from app.core import RMQManager
from app.core.db_manager import DBManager
from app.core.logs import logger
from app.db import async_session_maker
from app.services.bot import BotServices


class RmqHandlersService:

    def __init__(self, rmq: RMQManager):
        self.rmq = rmq
        self.db_manager = DBManager(session_factory=async_session_maker)

    async def admin_auth_response(self, id_: str, user: str, command: str):
        """
        Обработчик действий на аутентификацию админа
        """

        if not id_:
            logger.error("ID пользователя не задан")
            return

        if command == "ok":
            logger.info(f"Пользователь {user} ({id_}) одобрен")
            await BotServices(self.rmq).send_info(f"Пользователь <b>{user}</b> одобрен")

        elif command == "logout":
            logger.info(f"Команда отзыва jti-токенов пользователя {user} ({id_})")
            if await self._revoke_jti(id_):
                await BotServices(self.rmq).send_info(f"Jti-токены пользователя <b>{user}</b> отозваны")
            else:
                await BotServices(self.rmq).send_info(f"Ошибка отзыва jti-токенов пользователя <b>{user}</b>")

        elif command == "block":
            logger.info(f"Команда блокировки пользователя {user} ({id_})")
            if await self._block_user(id_):
                await BotServices(self.rmq).send_info(f"Пользователь <b>{user}</b> заблокирован")
            else:
                await BotServices(self.rmq).send_info(f"Ошибка блокировки пользователя <b>{user}</b>")

        else:
            logger.error(f"Неизвестная команда {command}")

    async def _revoke_jti(self, id_: str) -> bool:
        """
        Отзыв jti-токенов пользователя
        """

        try:
            user_id = UUID(id_)
            async with self.db_manager as db:
                await db.auth.refresh_tokens.delete(user_id=user_id, commit=True)
            return True

        except Exception as ex:
            logger.exception(ex)
            return False

    async def _block_user(self, id_: str) -> bool:
        """
        Блокировка учётной записи пользователя
        """

        try:
            user_id = UUID(id_)
            async with self.db_manager as db:
                await db.auth.refresh_tokens.delete(user_id=user_id)
                await db.users.update({"id": user_id, "is_active": False})
                await db.commit()
            return True

        except Exception as ex:
            logger.exception(ex)
            return False

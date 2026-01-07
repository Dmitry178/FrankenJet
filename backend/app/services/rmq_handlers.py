""" Обработчик сообщений от бота уведомлений через RabbitMQ """

from app.core import RMQManager
from app.core.logs import logger
from app.services.bot import BotServices


class RmqHandlersService:

    def __init__(self, rmq: RMQManager):
        self.rmq = rmq

    async def admin_auth_response(self, id_: str, user: str, result: str):
        """
        Обработчик действий на аутентификацию админа
        """

        if not id_:
            logger.error("ID обработчика не задан")
            return

        if result == "ok":
            logger.info(f"Пользователь {user} ({id_}) одобрен")
            await BotServices(self.rmq).send_info(f"Пользователь <b>{user}</b> одобрен")

        elif result == "logout":
            ...

        elif result == "block":
            ...

        else:
            logger.error(f"Неизвестная команда {result}")

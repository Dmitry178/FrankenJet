import json

from dataclasses import dataclass

from app.config.app import RMQ_FJ_OUTPUT_QUEUE
from app.config.env import settings
from app.core import RMQManager
from app.schemas.logs import SLogEntry


@dataclass
class MsgTypes:
    """
    Типы сообщений на отправку в бот
    """

    log = "log"
    info = "info"
    notification = "notification"
    auth_notification = "auth_notification"
    moderation = "moderation"


class BotServices:

    rmq: RMQManager | None

    def __init__(self, rmq: RMQManager | None = None) -> None:
        self.rmq = rmq

    async def send_message(self, msg_type: str, msg_data: dict | str) -> None:
        """
        Отправка подготовленного сообщения в RabbitMQ
        """

        data = {
            "type": msg_type,
            "data": msg_data,
        }

        try:
            await self.rmq.publish(
                json.dumps(data),
                queue=RMQ_FJ_OUTPUT_QUEUE,
            )
            return None

        except Exception as ex:
            # logger.exception(ex)
            raise ex

    async def send_logs(self, log_entry: SLogEntry) -> None:
        """
        Отправка логов в бот уведомлений
        """

        await self.send_message(MsgTypes.log, log_entry.model_dump())
        return None

    async def send_info(self, message: str) -> None:
        """
        Отправка технического сообщения в бот уведомлений
        """

        data = {
            "caption": f"{settings.APP_NAME} ({settings.APP_MODE})",
            "message": message
        }
        await self.send_message(MsgTypes.info, data)
        return None


bot_services = BotServices()

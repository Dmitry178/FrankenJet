import json

from dataclasses import dataclass

from app.config import RMQ_QUEUE, app_settings
from app.rmq_manager import AppRMQManager
from app.schemas import SLogEntry


@dataclass
class MsgTypes:
    """
    Типы сообщений на отправку в бот
    """

    log = "log"
    info = "info"


class AppBotServices:

    rmq: AppRMQManager | None

    def __init__(self, rmq: AppRMQManager | None = None) -> None:
        self.rmq = rmq

    async def _send_message(self, msg_type: str, msg_data: dict | str) -> None:
        """
        Отправка подготовленного сообщения в RabbitMQ
        """

        if not self.rmq:
            return

        data = {
            "type": msg_type,
            "data": msg_data,
        }

        try:
            await self.rmq.publish(
                json.dumps(data),
                queue=RMQ_QUEUE,
            )
            return None

        except Exception as ex:
            # app_logger.exception(ex)
            raise ex

    async def send_logs(self, log_entry: SLogEntry) -> None:
        """
        Отправка логов в бот уведомлений
        """

        if not self.rmq:
            return

        await self._send_message(MsgTypes.log, log_entry.model_dump())
        return None

    async def send_info(self, message: str) -> None:
        """
        Отправка технического сообщения в бот уведомлений
        """

        if not self.rmq:
            return

        data = {
            "caption": app_settings.APP_NAME,
            "message": message
        }
        await self._send_message(MsgTypes.info, data)
        return None


bot_services = AppBotServices()

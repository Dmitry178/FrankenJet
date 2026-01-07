import json

from app.config.app import RMQ_FJ_INPUT_QUEUE
from app.core import rmq_manager
from app.core.logs import logger
from app.services.rmq_handlers import RmqHandlersService


@rmq_manager.subscriber(RMQ_FJ_INPUT_QUEUE)
async def handle_backend_response(message: str):
    try:
        data = json.loads(message)

        if data.get("type") == "admin_auth_response":
            id_ = data.get("id")
            user = data.get("user")
            result = data.get("result")
            await RmqHandlersService(rmq_manager).admin_auth_response(id_, user, result)

        else:
            logger.info(f"Получено сообщение от бота уведомлений: {data}")

    except json.JSONDecodeError as ex:
        logger.exception("Ошибка декодирования json из RabbitMQ", extra={"error": str(ex)})

    except Exception as ex:
        logger.exception(ex)

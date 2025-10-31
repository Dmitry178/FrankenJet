""" Обработчики сообщений из RabbitMQ """

from faststream.rabbit import RabbitBroker

from app.broker.frankenjet import proceed_messages_from_frankenjet
from app.core.config import bot_settings, RMQ_FJ_OUTPUT_QUEUE

broker = RabbitBroker(
    url=bot_settings.RMQ_CONN,
)


@broker.subscriber(RMQ_FJ_OUTPUT_QUEUE)
async def handle_frankenjet(message: str):
    """
    Получение сообщений от FrankenJet
    """

    await proceed_messages_from_frankenjet(message)

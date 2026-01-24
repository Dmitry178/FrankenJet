""" Обработчики сообщений из RabbitMQ """

from faststream.rabbit import RabbitBroker

from app.broker.frankenjet import proceed_messages_from_frankenjet
from app.broker.vectorizer import proceed_messages_from_vectorizer
from app.core.config import bot_settings, RMQ_FJ_OUTPUT_QUEUE, RMQ_VECTORIZER_QUEUE

broker = RabbitBroker(
    url=bot_settings.RMQ_CONN,
)


@broker.subscriber(RMQ_FJ_OUTPUT_QUEUE)
async def handle_frankenjet(data: str):
    """
    Подписка на сообщения от Franken Jet
    """

    await proceed_messages_from_frankenjet(data)


@broker.subscriber(RMQ_VECTORIZER_QUEUE)
async def handle_vectorizer(data: str):
    """
    Подписка на сообщения от Vectorizer
    """

    await proceed_messages_from_vectorizer(data)

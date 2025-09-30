""" Роутер для проверки бота уведомлений """

import json

from fastapi import Body, Request, Depends, APIRouter

from app.api.openapi_examples import notification_example, moderation_example
from app.config.app import RMQ_NOTIFICATIONS_QUEUE, RMQ_ADMIN_AUTH_QUEUE, RMQ_MODERATION_QUEUE
from app.core import RMQManager
from app.core.logs import logger
from app.dependencies.auth import get_auth_user_info, get_auth_admin_id
from app.dependencies.rmq import get_rmq
from app.exceptions.bot import bot_user_forbidden_403
from app.schemas.bot import SBotNotification, SBotAuthNotification, SBotModeration
from app.types import status_ok, status_error

bot_router = APIRouter(prefix="/bot", tags=["Notification Bot"])


@bot_router.post(
    "/notifications",
    summary="Отправка уведомления в бот",
    # dependencies=[Depends(get_auth_admin_id)],  # отправить уведомление может только админ
)
async def send_notification(
        data: SBotNotification = Body(openapi_examples=notification_example),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка сообщения в бот уведомлений
    """

    if not rmq.url:
        return {**status_error, "detail": "RabbitMQ не установлен"}

    try:
        await rmq.publish(
            data.notification,
            queue=RMQ_NOTIFICATIONS_QUEUE,
        )
        return status_ok

    except Exception as ex:
        logger.exception(ex)
        return status_error


@bot_router.post(
    "/auth-notification",
    summary="Уведомление об аутентификации",
    dependencies=[Depends(get_auth_admin_id)],
)
async def send_auth_notification(
        request: Request,
        user_info=Depends(get_auth_user_info),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка сообщения в бот уведомлений об аутентификации пользователя
    """

    if not rmq.url:
        return {**status_error, "detail": "RabbitMQ не установлен"}

    try:
        roles = user_info.roles
        if "admin" not in roles:
            raise bot_user_forbidden_403

        client_ip = request.client.host
        user_agent = request.headers.get("user-agent")

        data = SBotAuthNotification(
            user_id=user_info.id,
            user_name=user_info.name,
            email=user_info.email,
            roles=user_info.roles,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        await rmq.broker.publish(
            json.dumps(data.model_dump(by_alias=True)),
            queue=RMQ_ADMIN_AUTH_QUEUE,
        )

        return status_ok

    except Exception as ex:
        logger.exception(ex)
        return status_error


@bot_router.post(
    "/moderation",
    summary="Модерация комментария",
    # dependencies=[Depends(get_auth_admin_id)],
)
async def send_comment_to_moderation(
        data: SBotModeration = Body(openapi_examples=moderation_example),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка комментария на модерацию в бот уведомлений
    """

    if not rmq.url:
        return {**status_error, "detail": "RabbitMQ не установлен"}

    try:
        json_data = {
            "id": data.id,
            "comment": data.comment,
        }

        await rmq.broker.publish(
            json.dumps(json_data),
            queue=RMQ_MODERATION_QUEUE,
        )
        return status_ok

    except Exception as ex:
        logger.exception(ex)
        return status_error

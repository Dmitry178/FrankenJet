""" Роутер для отправки сообщений в бот уведомлений (только для админа) """

from fastapi import Body, Depends, APIRouter
from starlette import status

from app.api.openapi_examples import notification_example, moderation_example
from app.core import RMQManager
from app.core.logs import logger
from app.dependencies.api import get_client_info
from app.dependencies.auth import get_auth_user_info, get_auth_admin_id
from app.dependencies.rmq import get_rmq
from app.exceptions.api import http_error_500, rabbitmq_not_available
from app.schemas.api import SClientInfo
from app.schemas.auth import SAuthUserInfo
from app.schemas.bot import SBotNotification, SBotAuthNotification, SBotModeration
from app.services.bot import BotServices, MsgTypes
from app.types import status_ok

bot_router = APIRouter(prefix="/bot", tags=["Notification Bot"])


@bot_router.post(
    "/notifications",
    summary="Отправка уведомления в бот",
    dependencies=[Depends(get_auth_admin_id)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_notification(
        data: SBotNotification = Body(openapi_examples=notification_example),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка сообщения в бот уведомлений
    """

    if not rmq.url:
        return rabbitmq_not_available

    try:
        await BotServices(rmq).send_message(MsgTypes.notification, data.notification)
        return status_ok

    except Exception as ex:
        logger.error(ex)
        return http_error_500


@bot_router.post(
    "/auth-notification",
    summary="Уведомление об аутентификации",
    dependencies=[Depends(get_auth_admin_id)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_auth_notification(
        user_info: SAuthUserInfo = Depends(get_auth_user_info),
        client_info: SClientInfo = Depends(get_client_info),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка сообщения в бот уведомлений об аутентификации пользователя
    """

    if not rmq.url:
        return rabbitmq_not_available

    try:
        data = SBotAuthNotification(
            user_id=user_info.id,
            user_name=user_info.name,
            email=user_info.email,
            roles=user_info.roles,
            client_ip=client_info.ip,
            user_agent=client_info.user_agent,
        )
        await BotServices(rmq).send_message(MsgTypes.auth_notification, data.model_dump(by_alias=True))
        return status_ok

    except Exception as ex:
        logger.exception(ex)
        return http_error_500


@bot_router.post(
    "/moderation",
    summary="Модерация комментария",
    dependencies=[Depends(get_auth_admin_id)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_comment_to_moderation(
        data: SBotModeration = Body(openapi_examples=moderation_example),
        rmq: RMQManager = Depends(get_rmq),
):
    """
    Отправка комментария на модерацию в бот уведомлений
    """

    if not rmq.url:
        return rabbitmq_not_available

    try:
        data = {
            "id": data.id,
            "comment": data.comment,
        }
        await BotServices(rmq).send_message(MsgTypes.moderation, data)
        return status_ok

    except Exception as ex:
        logger.exception(ex)
        return http_error_500

from fastapi import APIRouter, Path
from uuid import UUID

from app.core.logs import logger
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.services.chatbot import ChatBotServices
from app.types import status_ok

chat_bot_router = APIRouter(prefix="/chat", tags=["Chat Bot"])


@chat_bot_router.get("/history/{chat_id}", summary="История чата")
async def get_chat_history(
        db: DDB,
        chat_id: UUID = Path(..., description="ID чата"),
):
    """
    История чата пользователя
    """

    try:
        data = await ChatBotServices(db=db).get_history_for_bot(chat_id)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response

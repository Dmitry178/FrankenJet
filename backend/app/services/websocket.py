import json

from fastapi import WebSocket, WebSocketDisconnect
from uuid import UUID

from app.core import chatbot_settings
from app.core.db_manager import DBManager
from app.core.logs import logger
from app.core.ws_manager import WSManager
from app.dependencies.db import DDB
from app.schemas.refresh_tokens import SRefreshTokens
from app.services.chatbot import ChatBotServices


class WebSocketAuthService:
    """
    Websocket для работы с аутентифицированными пользователями
    """

    db: DBManager | None

    def __init__(self, ws_manager: WSManager, db: DBManager | None = None) -> None:
        self.ws_manager = ws_manager
        self.db = db

    async def handle_websocket_connection(self, user_id: UUID, websocket: WebSocket):
        await self.ws_manager.connect(user_id, websocket)

        try:
            while True:
                data = await websocket.receive_text()
                await self.process_websocket_message(user_id, data)

        except WebSocketDisconnect:
            self.ws_manager.disconnect(user_id, websocket)

    async def auth_ws(self, jti: UUID) -> UUID | None:
        """
        Проверка аутентификации пользователя через websocket
        """

        token: SRefreshTokens = self.db.auth.refresh_tokens.select_one_or_none(jti=jti)
        if not token:
            return None
        return token.user_id

    async def process_websocket_message(self, user_id: UUID, data: str):
        """
        Обработка входящих сообщений через websocket
        """

        try:
            print(user_id, data)
            # TODO сделать logout
            ...

        except (json.JSONDecodeError, Exception) as ex:
            logger.exception(ex)


class WebSocketBotService:
    """
    Websocket чат-бота
    """

    def __init__(self, ws_manager: WSManager, db: DDB):
        self.ws_manager = ws_manager
        self.db = db

    async def handle_websocket_connection(self, chat_id: UUID, websocket: WebSocket):
        await self.ws_manager.connect(chat_id, websocket)

        try:
            while True:
                data = await websocket.receive_text()
                await self.process_websocket_message(chat_id, data)

        except WebSocketDisconnect:
            self.ws_manager.disconnect(chat_id, websocket)

    async def process_websocket_message(self, chat_id: UUID, data: str):
        """
        Обработка входящих сообщений через websocket
        """

        try:
            data = json.loads(data)
            if data.get("type", "") == "message":
                message = data.get("message")
                await ChatBotServices(
                    db=self.db,
                    ws_manager=self.ws_manager,
                    bot_settings=chatbot_settings
                ).proceed_user_message(chat_id, message)

        except (json.JSONDecodeError, Exception) as ex:
            logger.exception(ex)

import json

from fastapi import WebSocket, WebSocketDisconnect
from uuid import UUID

from app.core import chatbot_settings
from app.core.db_manager import DBManager
from app.core.ws_manager import WSBotManager
from app.dependencies.db import DDB
from app.schemas.jti import SRefreshTokens
from app.services.chatbot import ChatBotServices
from scripts.init_db import logger


class WebSocketsAuthServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def auth_ws(self, jti: UUID) -> int | None:
        """
        Проверка аутентификации пользователя через веб-сокеты
        """

        token: SRefreshTokens = self.db.auth.refresh_tokens.select_one_or_none(jti=jti)
        if not token or token.revoked:
            return None
        return token.user_id


class WebSocketService:

    def __init__(self, ws_manager: WSBotManager, db: DDB):
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
            logger.error(ex)

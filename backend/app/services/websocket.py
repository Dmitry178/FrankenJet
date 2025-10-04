from fastapi import WebSocket, WebSocketDisconnect
from uuid import UUID

from app.core.db_manager import DBManager
from app.core.ws_manager import WSManager
from app.schemas.jti import SRefreshTokens


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

    def __init__(self, ws_manager: WSManager):
        self.ws_manager = ws_manager

    async def handle_websocket_connection(self, websocket: WebSocket, user_id: int, jti: UUID):
        await self.ws_manager.connect(user_id, jti, websocket)

        try:
            while True:
                data = await websocket.receive_text()
                await self.process_websocket_message(data, user_id, jti)

        except WebSocketDisconnect:
            self.ws_manager.disconnect(user_id, jti, websocket)

    async def process_websocket_message(self, data: str, user_id: int, jti: UUID | None = None):
        print(user_id, jti)
        await self.ws_manager.broadcast_to_user(user_id, f"User {user_id}: {data}")

""" Менеджер WebSocket """

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from uuid import UUID


class WSManager:
    def __init__(self):
        # user_id -> {jti -> [WebSocket, ...]}
        self.active_connections: Dict[int, Dict[UUID, List[WebSocket]]] = {}

    async def connect(self, user_id: int, jti: UUID, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        if jti not in self.active_connections[user_id]:
            self.active_connections[user_id][jti] = []
        self.active_connections[user_id][jti].append(websocket)

    def disconnect(self, user_id: int, jti: UUID, websocket: WebSocket):
        if user_id in self.active_connections:
            if jti in self.active_connections[user_id]:
                try:
                    self.active_connections[user_id][jti].remove(websocket)
                except ValueError:
                    pass
                if not self.active_connections[user_id][jti]:
                    del self.active_connections[user_id][jti]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def disconnect_jti(self, user_id: int, jti: UUID):
        """
        Отключение всех WebSocket-соединений по jti
        """

        if user_id in self.active_connections:
            if jti in self.active_connections[user_id]:
                for ws in self.active_connections[user_id][jti]:
                    await ws.close(code=1000)
                del self.active_connections[user_id][jti]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def disconnect_user(self, user_id: int):
        """
        Отключение всех WebSocket-соединений пользователя
        """

        if user_id in self.active_connections:
            for jti, ws_list in self.active_connections[user_id].items():
                for ws in ws_list:
                    await ws.close(code=1000)
            del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: int, message: str):
        """
        Отправка сообщения всем подключениям пользователя
        """

        if user_id in self.active_connections:
            for jti, ws_list in self.active_connections[user_id].items():
                for ws in ws_list:
                    try:
                        await ws.send_text(message)
                    except WebSocketDisconnect:
                        self.disconnect(user_id, jti, ws)


ws_manager = WSManager()

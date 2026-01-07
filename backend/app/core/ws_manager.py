""" Менеджер WebSocket """

import json

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from uuid import UUID

from app.core.logs import logger


class WSManager:
    def __init__(self):
        # {connection_id: [WebSocket, ...]}
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, connection_id: UUID, websocket: WebSocket):
        await websocket.accept()

        # создание списка подключений для connection_id, если его нет
        if connection_id not in self.active_connections:
            self.active_connections[connection_id] = []

        self.active_connections[connection_id].append(websocket)

    def disconnect(self, connection_id: UUID, websocket: WebSocket):
        if connection_id in self.active_connections:
            try:
                self.active_connections[connection_id].remove(websocket)
            except ValueError:
                logger.info("Подключение уже удалено")

            # удаление connection_id, если список подключений пуст
            if not self.active_connections[connection_id]:
                del self.active_connections[connection_id]

    async def send_message_to_connection(self, connection_id: UUID, message: str):
        """
        Отправка сообщения в connection_id
        """

        if connection_id in self.active_connections:
            for websocket in self.active_connections[connection_id]:
                try:
                    data = {
                        "type": "answer",
                        "text": message,
                    }
                    await websocket.send_text(json.dumps(data))

                except WebSocketDisconnect:
                    # обработка отключившихся websocket в реальном времени
                    self.disconnect(connection_id, websocket)

    async def broadcast_message(self, message: str):
        """
        Отправка сообщения всем активным подключениям
        """

        for connections in list(self.active_connections.values()):
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    pass

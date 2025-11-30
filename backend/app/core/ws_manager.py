""" Менеджер WebSocket """

import json

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from uuid import UUID

from app.core.logs import logger


class WSBotManager:
    def __init__(self):
        # {chat_id: [WebSocket, ...]}
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, chat_id: UUID, websocket: WebSocket):
        await websocket.accept()

        # создание списка подключений для chat_id, если его нет
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []

        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: UUID, websocket: WebSocket):
        if chat_id in self.active_connections:
            try:
                self.active_connections[chat_id].remove(websocket)
            except ValueError:
                logger.info("Подключение уже удалено")

            # удаление chat_id, если список подключений пуст
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def send_message_to_chat(self, chat_id: UUID, message: str):
        """
        Отправка сообщения в chat_id
        """

        if chat_id in self.active_connections:
            for websocket in self.active_connections[chat_id]:
                try:
                    data = {
                        "type": "answer",
                        "text": message,
                    }
                    await websocket.send_text(json.dumps(data))

                except WebSocketDisconnect:
                    # обработка отключившихся websocket в реальном времени
                    self.disconnect(chat_id, websocket)

    async def broadcast_message(self, message: str):
        """
        Отправка сообщения всем активным подключениям
        """

        for chat_connections in list(self.active_connections.values()):
            for websocket in chat_connections:
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    pass

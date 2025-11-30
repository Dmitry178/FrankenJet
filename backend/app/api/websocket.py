from fastapi import APIRouter, WebSocket
from uuid import UUID

from app.core import ws_manager
from app.dependencies.db import DDB
from app.services.websocket import WebSocketService

ws_router = APIRouter()


@ws_router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: UUID, db: DDB):
    await WebSocketService(ws_manager, db).handle_websocket_connection(chat_id, websocket)

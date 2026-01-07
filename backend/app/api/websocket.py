from fastapi import APIRouter, WebSocket
from uuid import UUID

from app.core import ws_manager
from app.dependencies.db import DDB
from app.services.websocket import WebSocketAuthService, WebSocketBotService

ws_router = APIRouter()


@ws_router.websocket("/ws/auth/{user_id}")
async def auth_websocket_endpoint(websocket: WebSocket, user_id: UUID, db: DDB):
    await WebSocketAuthService(ws_manager, db).handle_websocket_connection(user_id, websocket)


@ws_router.websocket("/ws/chat/{chat_id}")
async def chat_websocket_endpoint(websocket: WebSocket, chat_id: UUID, db: DDB):
    await WebSocketBotService(ws_manager, db).handle_websocket_connection(chat_id, websocket)

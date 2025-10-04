from fastapi import APIRouter, WebSocket
from uuid import UUID

from app.core.ws_manager import ws_manager
from app.dependencies.db import DDB
from app.services.websocket import WebSocketsAuthServices, WebSocketService

ws_router = APIRouter()


@ws_router.websocket("/ws/{jti}")
async def websocket_endpoint(websocket: WebSocket, jti: UUID, db: DDB):
    if not (user_id := await WebSocketsAuthServices(db).auth_ws(jti)):
        await websocket.close(code=1008)
        return

    await ws_manager.connect(user_id, jti, websocket)
    await WebSocketService(ws_manager).handle_websocket_connection(websocket, user_id, jti)

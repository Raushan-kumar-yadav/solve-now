import json
import asyncio
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from core.database import get_db
from core.config import settings
from core.redis import pubsub_manager
from models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections across rooms.
    Uses Redis pub/sub for cross-worker message distribution.
    Maps: room_id -> user_id -> set[WebSocket] (supports multiple tabs per user)
    """

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            # Start Redis subscriber for this room on first connection
            self.pubsub_tasks[room_id] = asyncio.create_task(
                self.subscribe_to_room(room_id)
            )

        if user_id not in self.active_connections[room_id]:
            self.active_connections[room_id][user_id] = set()

        self.active_connections[room_id][user_id].add(websocket)

        # Broadcast presence to room
        await self.broadcast_to_room(room_id, {
            "type": "presence.updated",
            "payload": {"user_id": user_id, "status": "online"},
        })
        logger.debug(f"WS connected: user={user_id} room={room_id}")

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.active_connections:
            if user_id in self.active_connections[room_id]:
                self.active_connections[room_id][user_id].discard(websocket)
                if not self.active_connections[room_id][user_id]:
                    del self.active_connections[room_id][user_id]

    async def handle_disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        self.disconnect(websocket, room_id, user_id)

        # Broadcast offline status if user has no remaining connections in room
        if room_id in self.active_connections and user_id not in self.active_connections[room_id]:
            await self.broadcast_to_room(room_id, {
                "type": "presence.updated",
                "payload": {"user_id": user_id, "status": "offline"},
            })

        # Clean up empty rooms and cancel their Redis subscriber
        if room_id in self.active_connections and not self.active_connections[room_id]:
            del self.active_connections[room_id]
            if room_id in self.pubsub_tasks:
                self.pubsub_tasks[room_id].cancel()
                del self.pubsub_tasks[room_id]

        logger.debug(f"WS disconnected: user={user_id} room={room_id}")

    async def broadcast_to_room(self, room_id: str, message: dict):
        """Publish message to Redis channel — distributed to all workers."""
        await pubsub_manager.publish(f"room:{room_id}", message)

    async def subscribe_to_room(self, room_id: str):
        """Subscribe to Redis channel and forward messages to local WebSocket connections."""
        try:
            async for message in pubsub_manager.subscribe(f"room:{room_id}"):
                if room_id not in self.active_connections:
                    break
                for user_conns in list(self.active_connections[room_id].values()):
                    for ws in list(user_conns):
                        try:
                            await ws.send_json(message)
                        except Exception:
                            # Stale connection — will be cleaned up on next disconnect event
                            pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis subscription error for room={room_id}: {e}")


manager = ConnectionManager()


async def _authenticate_websocket(websocket: WebSocket, db: Session) -> User | None:
    """
    Authenticate a WebSocket connection via HTTP-only cookie.
    Returns User or None. Never raises — caller is responsible for closing.
    """
    token = websocket.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None
        # Check denylist
        from models.security import TokenDenylist
        if db.query(TokenDenylist).filter(TokenDenylist.token == token).first():
            return None
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except (JWTError, Exception):
        return None


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room_endpoint(
    websocket: WebSocket,
    room_id: str,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for collaborative room chat.
    Authenticates via cookie. Broadcasts typing events via Redis.
    """
    user = await _authenticate_websocket(websocket, db)
    if not user:
        await websocket.close(code=1008, reason="Authentication required")
        return

    user_id_str = str(user.id)
    await manager.connect(websocket, room_id, user_id_str)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                event_type = parsed.get("type")

                if event_type in ("typing.started", "typing.stopped"):
                    # Broadcast typing indicator — use username not email for privacy
                    await manager.broadcast_to_room(room_id, {
                        "type": event_type,
                        "payload": {
                            "user_id": user_id_str,
                            "name": user.username or "Someone",  # Never expose raw email
                        },
                    })
            except (json.JSONDecodeError, KeyError):
                pass  # Malformed client message — ignore silently
    except WebSocketDisconnect:
        await manager.handle_disconnect(websocket, room_id, user_id_str)


@router.websocket("/ws/users/{target_user_id}")
async def websocket_user_channel(
    websocket: WebSocket,
    target_user_id: str,
    db: Session = Depends(get_db),
):
    """
    Personal WebSocket channel for real-time notifications.
    Users can only connect to their own channel.
    """
    user = await _authenticate_websocket(websocket, db)
    if not user or str(user.id) != target_user_id:
        await websocket.close(code=1008, reason="Authentication required")
        return

    room_id = f"user_channel:{target_user_id}"
    await manager.connect(websocket, room_id, target_user_id)

    try:
        while True:
            # Personal channel is receive-only — client sends nothing meaningful
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.handle_disconnect(websocket, room_id, target_user_id)
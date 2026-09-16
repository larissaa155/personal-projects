from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket connection manager for real-time communication
    """
    
    def __init__(self):
        #active_connections: {user_id: [WebSocket, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        #room_connections: {room_id: [user_id, ...]}
        self.room_connections: Dict[str, List[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept connection and add to active connections"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        logger.info(f"User {user_id} connected. Total connections: {self.get_total_connections()}")
        
        #Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "message": "Connected to TaskFlow WebSocket",
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
            #Remove from rooms
            for room_id, users in self.room_connections.items():
                if user_id in users:
                    users.remove(user_id)
                    
        logger.info(f"User {user_id} disconnected. Total connections: {self.get_total_connections()}")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast(self, message: Dict[str, Any], exclude_user: Optional[int] = None):
        """Send message to all connected users"""
        for user_id, connections in self.active_connections.items():
            if user_id == exclude_user:
                continue
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
    
    async def send_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: Optional[int] = None):
        """Send message to all users in a room"""
        if room_id in self.room_connections:
            for user_id in self.room_connections[room_id]:
                if user_id == exclude_user:
                    continue
                await self.send_personal_message(message, user_id)
    
    async def join_room(self, room_id: str, user_id: int):
        """Add user to a room"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        if user_id not in self.room_connections[room_id]:
            self.room_connections[room_id].append(user_id)
            
        #Notify other users in the room
        await self.send_to_room(
            room_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
    
    async def leave_room(self, room_id: str, user_id: int):
        """Remove user from a room"""
        if room_id in self.room_connections:
            if user_id in self.room_connections[room_id]:
                self.room_connections[room_id].remove(user_id)
                
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_online_users(self) -> List[int]:
        """Get list of online user IDs"""
        return list(self.active_connections.keys())

#Global connection manager instance
manager = ConnectionManager()

#WebSocket endpoint handler
async def websocket_handler(websocket: WebSocket, user_id: int):
    """Handle WebSocket connections"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            #Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    #Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == "join_room":
                    room_id = message.get("room_id")
                    if room_id:
                        await manager.join_room(room_id, user_id)
                        await websocket.send_json({
                            "type": "joined_room",
                            "room_id": room_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif message_type == "leave_room":
                    room_id = message.get("room_id")
                    if room_id:
                        await manager.leave_room(room_id, user_id)
                        await websocket.send_json({
                            "type": "left_room",
                            "room_id": room_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif message_type == "task_update":
                    #Broadcast task update to relevant users
                    task_id = message.get("task_id")
                    task_data = message.get("data", {})
                    
                    #Send to task-specific room
                    await manager.send_to_room(
                        f"task_{task_id}",
                        {
                            "type": "task_updated",
                            "task_id": task_id,
                            "data": task_data,
                            "updated_by": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    
                    #Also broadcast to team room if specified
                    if "team_id" in task_data:
                        await manager.send_to_room(
                            f"team_{task_data['team_id']}",
                            {
                                "type": "team_task_updated",
                                "task_id": task_id,
                                "data": task_data,
                                "updated_by": user_id,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                
                elif message_type == "comment":
                    #Handle comment notifications
                    task_id = message.get("task_id")
                    comment_data = message.get("data", {})
                    
                    #Send to task comment room
                    await manager.send_to_room(
                        f"task_{task_id}_comments",
                        {
                            "type": "new_comment",
                            "task_id": task_id,
                            "data": comment_data,
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                
                else:
                    #Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)
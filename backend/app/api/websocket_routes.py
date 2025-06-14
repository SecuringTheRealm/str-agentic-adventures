"""
WebSocket routes for real-time game updates.

This implementation provides real-time multiplayer communication using FastAPI's
native WebSocket support, as per the updated ADR 0008 decision.
"""

import logging
import json
from typing import Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.campaign_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, campaign_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)

        if campaign_id:
            if campaign_id not in self.campaign_connections:
                self.campaign_connections[campaign_id] = []
            self.campaign_connections[campaign_id].append(websocket)

        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket, campaign_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if campaign_id and campaign_id in self.campaign_connections:
            if websocket in self.campaign_connections[campaign_id]:
                self.campaign_connections[campaign_id].remove(websocket)

            # Clean up empty campaign connection lists
            if not self.campaign_connections[campaign_id]:
                del self.campaign_connections[campaign_id]

        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send personal message: {str(e)}")

    async def send_campaign_message(self, message: str, campaign_id: str):
        if campaign_id in self.campaign_connections:
            disconnected = []
            for connection in self.campaign_connections[campaign_id]:
                if connection.client_state == WebSocketState.CONNECTED:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(f"Failed to send campaign message: {str(e)}")
                        disconnected.append(connection)
                else:
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, campaign_id)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast message: {str(e)}")
                    disconnected.append(connection)
            else:
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager
manager = ConnectionManager()

# WebSocket router
router = APIRouter()


@router.websocket("/ws/chat/{campaign_id}")
async def chat_websocket(websocket: WebSocket, campaign_id: str):
    """WebSocket endpoint for streaming chat responses."""
    await manager.connect(websocket, campaign_id)
    try:
        while True:
            # Listen for chat messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_chat_message(message, websocket, campaign_id)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket,
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, campaign_id)
        logger.info(f"Client disconnected from chat in campaign {campaign_id}")


@router.websocket("/ws/{campaign_id}")
async def campaign_websocket(websocket: WebSocket, campaign_id: str):
    """WebSocket endpoint for campaign-specific real-time updates (non-chat)."""
    await manager.connect(websocket, campaign_id)
    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket, campaign_id)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket,
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, campaign_id)
        logger.info(f"Client disconnected from campaign {campaign_id}")


@router.websocket("/ws/global")
async def global_websocket(websocket: WebSocket):
    """WebSocket endpoint for global updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket,
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from global websocket")


async def handle_chat_message(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str
):
    """Handle incoming chat messages and stream AI responses."""
    try:
        message_type = message.get("type")
        
        if message_type == "chat_input":
            await handle_chat_input(message, websocket, campaign_id)
        elif message_type == "ping":
            await manager.send_personal_message(
                json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                websocket,
            )
        else:
            await manager.send_personal_message(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown chat message type: {message_type}",
                    }
                ),
                websocket,
            )
    except Exception as e:
        logger.error(f"Error handling chat message: {str(e)}")
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Failed to process chat message"}),
            websocket,
        )


async def handle_chat_input(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str
):
    """Handle chat input and stream AI response."""
    try:
        user_input = message.get("message", "")
        character_id = message.get("character_id")
        
        if not user_input.strip():
            await manager.send_personal_message(
                json.dumps({"type": "chat_error", "message": "Empty message"}),
                websocket,
            )
            return
            
        if not character_id:
            await manager.send_personal_message(
                json.dumps({"type": "chat_error", "message": "Missing character_id"}),
                websocket,
            )
            return

        # Send acknowledgment that we received the message
        await manager.send_personal_message(
            json.dumps({
                "type": "chat_start",
                "message": "Processing your input..."
            }),
            websocket,
        )

        # Import here to avoid circular imports
        from app.agents.dungeon_master_agent import get_dungeon_master
        
        # Get DM agent and stream response
        dm_agent = get_dungeon_master()
        
        # Create context for DM processing
        context = {
            "character_id": character_id,
            "campaign_id": campaign_id,
            "websocket": websocket,
            "streaming": True
        }
        
        # Process input with streaming enabled
        await dm_agent.process_input_stream(user_input, context)

    except Exception as e:
        logger.error(f"Error handling chat input: {str(e)}")
        await manager.send_personal_message(
            json.dumps({
                "type": "chat_error", 
                "message": f"Failed to process chat input: {str(e)}"
            }),
            websocket,
        )


async def handle_websocket_message(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str = None
):
    """Handle incoming WebSocket messages."""
    try:
        message_type = message.get("type")

        if message_type == "dice_roll":
            await handle_dice_roll(message, websocket, campaign_id)
        elif message_type == "game_update":
            await handle_game_update(message, websocket, campaign_id)
        elif message_type == "character_update":
            await handle_character_update(message, websocket, campaign_id)
        elif message_type == "ping":
            await manager.send_personal_message(
                json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                websocket,
            )
        else:
            await manager.send_personal_message(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                ),
                websocket,
            )
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {str(e)}")
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": "Failed to process message"}),
            websocket,
        )


async def handle_dice_roll(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str = None
):
    """Handle dice roll messages."""
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        dice_notation = message.get("notation", "1d20")
        character_id = message.get("character_id")
        skill = message.get("skill")
        player_name = message.get("player_name", "Player")

        rules_engine = RulesEnginePlugin()

        if character_id:
            # Get character for enhanced roll
            from app.agents.scribe_agent import get_scribe

            character = await get_scribe().get_character(character_id)
            if "error" not in character:
                result = rules_engine.roll_with_character(
                    dice_notation, character, skill
                )
            else:
                result = rules_engine.roll_dice(dice_notation)
        else:
            result = rules_engine.roll_dice(dice_notation)

        # Broadcast the result to all players in the campaign
        response = {
            "type": "dice_result",
            "player_name": player_name,
            "notation": dice_notation,
            "result": result,
            "skill": skill,
            "timestamp": result.get("timestamp"),
        }

        if campaign_id:
            await manager.send_campaign_message(json.dumps(response), campaign_id)
        else:
            await manager.send_personal_message(json.dumps(response), websocket)

    except Exception as e:
        logger.error(f"Error handling dice roll: {str(e)}")
        await manager.send_personal_message(
            json.dumps({"type": "error", "message": f"Failed to roll dice: {str(e)}"}),
            websocket,
        )


async def handle_game_update(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str = None
):
    """Handle game state updates."""
    try:
        update_type = message.get("update_type")
        data = message.get("data", {})

        response = {
            "type": "game_update",
            "update_type": update_type,
            "data": data,
            "timestamp": message.get("timestamp"),
        }

        if campaign_id:
            await manager.send_campaign_message(json.dumps(response), campaign_id)
        else:
            await manager.broadcast(json.dumps(response))

    except Exception as e:
        logger.error(f"Error handling game update: {str(e)}")


async def handle_character_update(
    message: Dict[str, Any], websocket: WebSocket, campaign_id: str = None
):
    """Handle character updates."""
    try:
        character_id = message.get("character_id")
        update_data = message.get("data", {})

        response = {
            "type": "character_update",
            "character_id": character_id,
            "data": update_data,
            "timestamp": message.get("timestamp"),
        }

        if campaign_id:
            await manager.send_campaign_message(json.dumps(response), campaign_id)
        else:
            await manager.send_personal_message(json.dumps(response), websocket)

    except Exception as e:
        logger.error(f"Error handling character update: {str(e)}")


# Utility functions for broadcasting updates
async def broadcast_dice_roll(
    campaign_id: str, player_name: str, notation: str, result: Dict[str, Any]
):
    """Broadcast a dice roll result to all players in a campaign."""
    response = {
        "type": "dice_result",
        "player_name": player_name,
        "notation": notation,
        "result": result,
        "timestamp": result.get("timestamp"),
    }
    await manager.send_campaign_message(json.dumps(response), campaign_id)


async def broadcast_game_state_update(
    campaign_id: str, update_type: str, data: Dict[str, Any]
):
    """Broadcast a game state update to all players in a campaign."""
    import datetime

    response = {
        "type": "game_update",
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    await manager.send_campaign_message(json.dumps(response), campaign_id)


async def broadcast_character_update(
    campaign_id: str, character_id: str, update_data: Dict[str, Any]
):
    """Broadcast a character update to all players in a campaign."""
    import datetime

    response = {
        "type": "character_update",
        "character_id": character_id,
        "data": update_data,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    await manager.send_campaign_message(json.dumps(response), campaign_id)

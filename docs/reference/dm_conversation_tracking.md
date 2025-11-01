# Dungeon Master Conversation Tracking

## Overview

This document describes how the Dungeon Master (DM) agent currently tracks and manages conversations with players in the AI Dungeon Master application.

**Last Updated**: 2025-11-01
**Status**: Current Implementation Analysis

## Current Implementation Summary

The Dungeon Master agent currently operates in a **stateless conversation model** with **no persistent storage** of conversation history.

### Key Findings

1. **No Database Storage**: Conversation messages are not persisted to the database
2. **Stateless Processing**: Each player message is processed independently without conversation context
3. **No Conversation History**: Previous messages are not retained or referenced in subsequent interactions
4. **Real-time Streaming Only**: Messages are streamed via WebSocket but not stored
5. **Unused Thread Support**: Azure AI thread capabilities exist but are not utilized

## Architecture Components

### 1. DungeonMasterAgent (`backend/app/agents/dungeon_master_agent.py`)

The DM agent is responsible for processing player inputs and generating responses.

**Key Methods:**
- `process_input(user_input, context)` - Non-streaming message processing
- `process_input_stream(user_input, context)` - WebSocket streaming processing
- `_stream_ai_response(messages, websocket)` - Azure OpenAI response streaming

**Conversation Flow:**

```python
# Current implementation (simplified)
async def process_input(self, user_input: str, context: dict[str, Any]):
    # 1. Create system prompt with character context
    system_prompt = self._get_dm_system_prompt(context)

    # 2. Create messages array (NO HISTORY)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 3. Send to Azure OpenAI
    ai_response = await self.azure_client.chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    # 4. Return response (NOT STORED)
    return {"message": ai_response.strip(), ...}
```

**What's Missing:**
- No conversation history loading
- No message history appended to context
- No storage of responses after generation
- Each request is treated as a fresh conversation

### 2. WebSocket Handler (`backend/app/api/websocket_routes.py`)

The WebSocket system manages real-time message delivery but does not persist conversations.

**Flow:**
1. Client connects to `/ws/chat/{campaign_id}`
2. Client sends message with `type: "chat_input"`
3. Handler extracts `user_input` and `character_id`
4. Handler calls `dm_agent.process_input_stream()`
5. DM streams response back through WebSocket
6. **Message is NOT stored after streaming completes**

**Code Reference** (`websocket_routes.py:195-238`):
```python
async def handle_chat_input(message, websocket, campaign_id):
    user_input = message.get("message", "")
    character_id = message.get("character_id")

    # Create context (no conversation history included)
    context = {
        "character_id": character_id,
        "campaign_id": campaign_id,
        "websocket": websocket,
        "streaming": True,
    }

    # Process with NO previous context
    await dm_agent.process_input_stream(user_input, context)
```

### 3. Database Models (`backend/app/models/db_models.py`)

**Current Tables:**
- `characters` - Character sheet data
- `campaigns` - Campaign metadata and settings
- `npcs` - Non-player character data
- `npc_interactions` - NPC interaction logs
- `spells` - Spell definitions

**Notable Absence:**
- ❌ No `messages` table
- ❌ No `conversations` table
- ❌ No `chat_history` table

**Campaign Model** (`game_models.py:312-334`):
```python
class Campaign(BaseModel):
    # ... other fields ...
    session_log: list[dict[str, Any]] = []  # UNUSED in current implementation
```

The `session_log` field exists in the Pydantic model but is:
- Not populated by the DM agent
- Not stored in the database
- Not referenced during message processing

### 4. Azure AI Thread Support (`backend/app/agent_framework_base.py`)

The `AgentFrameworkManager` provides thread management capabilities that are **not currently utilized**.

**Available but Unused:**
```python
def create_thread(self) -> AgentThread | None:
    """Create a new conversation thread for agent interactions."""
    client = self.get_agents_client()
    thread = client.threads.create()
    return thread
```

**Status**: The DM agent does not create or use Azure AI threads for conversation continuity.

## Conversation Context

### What IS Included in Each Request

The DM receives limited context for each message:

**From `context` parameter:**
- `character_name` - Player character name
- `character_level` - Character level
- `character_class` - Character class
- `campaign_id` - Current campaign ID
- `character_id` - Character ID

**System Prompt** (`dungeon_master_agent.py:67-104`):
The system prompt includes:
- DM role description and responsibilities
- Character information (name, level, class)
- General D&D 5e guidance
- Response style guidelines

### What IS NOT Included

- ❌ Previous messages from the player
- ❌ Previous responses from the DM
- ❌ Conversation history
- ❌ Session narrative context
- ❌ Campaign story progress
- ❌ Long-term memory of events

## Impact on User Experience

### Limitations

1. **No Memory**: DM cannot reference previous conversations
2. **Repetitive Responses**: May repeat information or ask for details already provided
3. **Lost Context**: Cannot build on previous narrative threads
4. **No Story Continuity**: Cannot track ongoing quests or plot developments
5. **Character Development**: Cannot remember character choices or personality traits shown in previous sessions

### Example Scenario

```
Player: "I want to explore the haunted castle we heard about in the tavern."
DM: "You approach a mysterious castle in the distance..."

[Next message - 2 minutes later]
Player: "I knock on the castle door."
DM: [Has no memory this is the same castle or that player was already there]
```

## Fallback Mode

When Azure OpenAI is not configured, the DM operates in **fallback mode** with canned responses.

**Fallback Implementation** (`dungeon_master_agent.py:366-406`):
- Simple pattern matching (e.g., "roll", "attack")
- Pre-defined response templates
- No AI generation
- Still no conversation history

## Technical Debt & Opportunities

### Immediate Issues

1. **State Management**: No mechanism to maintain conversation state
2. **Context Loss**: Each message loses all previous context
3. **Unused Infrastructure**: Thread management exists but isn't used
4. **Database Schema Gap**: No tables to store message history

### Potential Improvements

1. **Add Message Storage**: Create database tables for conversation history
2. **Implement Thread Management**: Use Azure AI threads for persistent context
3. **Session Log Integration**: Populate and use the `session_log` field
4. **Message History Loading**: Include recent messages in each request
5. **Conversation Summarization**: Summarize long conversations for context
6. **Memory System**: Implement long-term memory for campaigns

## Related Components

### Scribe Agent
The Scribe agent (`backend/app/agents/scribe_agent.py`) manages game data but also does not track conversations.

### NPC Interactions
NPC interactions ARE logged in the database (`npc_interactions` table), showing that selective persistence is already implemented for some interactions.

**Code Reference** (`db_models.py:75-88`):
```python
class NPCInteraction(Base):
    __tablename__ = "npc_interactions"

    id = Column(String, primary_key=True)
    npc_id = Column(String, ForeignKey("npcs.id"), nullable=False)
    character_id = Column(String, ForeignKey("characters.id"), nullable=True)
    interaction_type = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    data = Column(JSON, nullable=False)
```

## Recommendations

### Short-term
1. Document this limitation in user-facing documentation
2. Set user expectations about conversation memory
3. Consider adding session summaries to campaign metadata

### Medium-term
1. Implement basic message history storage
2. Include last N messages in DM context
3. Use Azure AI threads for conversation continuity

### Long-term
1. Build comprehensive memory system
2. Implement conversation summarization
3. Add semantic search for relevant context retrieval
4. Track narrative state and story progress

## References

- **DM Agent**: `backend/app/agents/dungeon_master_agent.py`
- **WebSocket Handler**: `backend/app/api/websocket_routes.py`
- **Database Models**: `backend/app/models/db_models.py`
- **Game Models**: `backend/app/models/game_models.py`
- **Agent Framework**: `backend/app/agent_framework_base.py`
- **ADR-0018**: Azure AI Agents SDK Adoption (`docs/adr/0018-azure-ai-agents-sdk-adoption.md`)

## Conclusion

The current implementation provides real-time, stateless interactions with the DM but does not maintain conversation history or context between messages. While this architecture is simple and functional, it significantly limits the quality of storytelling and narrative continuity that users would expect from a D&D-style experience.

Future enhancements should prioritize adding conversation persistence and context management to enable the DM to provide a more coherent and immersive gameplay experience.

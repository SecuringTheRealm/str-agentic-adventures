# NPC Management System Documentation

## Overview

The NPC Management System provides comprehensive functionality for creating, managing, and interacting with Non-Player Characters (NPCs) in the AI Dungeon Master application. The system includes personality modeling, behavior simulation, relationship tracking, and interaction capabilities.

## Architecture

The NPC management system consists of three main components:

1. **Data Models** (`app/models/game_models.py`) - Comprehensive data structures for NPCs
2. **Core Plugin** (`app/plugins/npc_management_plugin.py`) - Low-level NPC management functions
3. **Integration Service** (`app/services/npc_integration_service.py`) - High-level interface for game agents
4. **API Endpoints** (`app/api/npc_routes.py`) - REST API for NPC management

## Core Features

### 1. NPC Creation and Management

NPCs can be created with comprehensive attributes including:

- **Basic Information**: Name, description, race, role, location
- **Personality**: Personality type (friendly, hostile, neutral, etc.)
- **Behavior**: Trust level, bravery, intelligence, helpfulness, conversation style
- **Physical Attributes**: Abilities, hit points, armor class, age, appearance
- **Social Connections**: Relationships with characters and other NPCs
- **Memory**: Important facts, player interactions, witnessed events, rumors, secrets
- **Inventory**: Items, gold, trading preferences
- **Quest Integration**: Available quests, quest involvement

### 2. Personality and Behavior Modeling

NPCs have sophisticated personality and behavior systems:

#### Personality Types
- `FRIENDLY` - Welcoming and helpful
- `NEUTRAL` - Balanced disposition 
- `HOSTILE` - Aggressive or unwelcoming
- `SUSPICIOUS` - Distrustful and cautious
- `HELPFUL` - Eager to assist
- `GREEDY` - Motivated by material gain
- `PROUD` - Arrogant and self-important
- `HUMBLE` - Modest and self-effacing
- `CURIOUS` - Inquisitive and interested
- `FEARFUL` - Anxious and easily scared

#### Behavior Attributes
- **Trust Level** (0-10): How trusting the NPC is
- **Bravery** (0-10): How brave the NPC is in dangerous situations
- **Intelligence** (0-10): Affects dialogue complexity and problem-solving
- **Helpfulness** (0-10): Willingness to help players
- **Combat Behavior**: How the NPC acts in combat (aggressive, defensive, flee, support)
- **Conversation Style**: How the NPC speaks (polite, gruff, eloquent, simple, cryptic)

### 3. Relationship Tracking

The system tracks relationships between NPCs and characters with multiple dimensions:

- **Affection** (-10 to +10): How much the NPC likes the character
- **Trust** (-10 to +10): How much the NPC trusts the character
- **Respect** (-10 to +10): How much the NPC respects the character
- **Relationship Type**: friend, enemy, neutral, family, employer, etc.
- **History**: Record of significant interactions
- **Last Interaction**: Timestamp of most recent interaction

### 4. Memory System

NPCs maintain memories of:
- **Important Facts**: Key information they know
- **Player Interactions**: History of interactions with characters
- **Witnessed Events**: Events they've seen happen
- **Rumors Heard**: Information they've heard from others
- **Secrets Known**: Confidential information they possess

### 5. Role-Based Behavior

NPCs have predefined roles that influence their behavior:

- `MERCHANT` - Trades goods, shares commercial information
- `GUARD` - Enforces rules, patrols areas
- `INNKEEPER` - Provides lodging, shares local news
- `NOBLE` - Commands respect, has political influence
- `COMMONER` - General background character
- `CRIMINAL` - Operates outside the law
- `SCHOLAR` - Possesses academic knowledge
- `PRIEST` - Provides spiritual guidance
- `ARTISAN` - Creates and repairs items
- `SOLDIER` - Military background and training
- `QUEST_GIVER` - Provides quests to players
- `ALLY` - Supports and assists players
- `RIVAL` - Competes with or opposes players

## API Usage

### REST API Endpoints

#### Create NPC
```http
POST /api/npc
Content-Type: application/json

{
  "name": "Gareth the Innkeeper",
  "description": "A friendly innkeeper with a warm smile",
  "race": "human",
  "role": "innkeeper",
  "current_location": "The Prancing Pony Inn",
  "personality": "friendly"
}
```

#### Get NPC Details
```http
GET /api/npc/{npc_id}
```

#### Interact with NPC
```http
POST /api/npc/{npc_id}/interact
Content-Type: application/json

{
  "character_id": "char_123",
  "interaction_type": "conversation",
  "message": "Hello, do you have any rooms available?"
}
```

#### Update NPC Relationship
```http
PUT /api/npc/{npc_id}/relationship/{character_id}
Content-Type: application/json

{
  "affection_change": 2,
  "trust_change": 1,
  "event_description": "Character was polite and courteous"
}
```

#### Get NPCs in Location
```http
GET /api/npcs/location/{location}
```

#### List All NPCs
```http
GET /api/npcs
```

### Integration Service Usage

For game agents, use the NPC Integration Service for high-level operations:

```python
from app.services.npc_integration_service import npc_service

# Create a story NPC
result = npc_service.create_story_npc(
    name="Elara the Wise",
    description="An elderly elven scholar",
    location="The Grand Library",
    role_in_story="quest_giver",
    personality_traits=["wise", "helpful", "mysterious"]
)

# Get NPCs for a scene
npcs = npc_service.get_npcs_for_scene(
    location="The Grand Library",
    scene_context="Players seek ancient knowledge"
)

# Handle NPC interaction
interaction = npc_service.handle_npc_interaction(
    npc_name_or_id="Elara the Wise",
    character_id="char_456",
    interaction_type="conversation",
    player_action="I seek knowledge about ancient artifacts",
    scene_context="Player respectfully approaches"
)

# Update NPC story state
npc_service.update_npc_story_state(
    npc_name_or_id="Elara the Wise",
    story_event="Player helped recover stolen tome",
    impact_on_npc="Greatly appreciates assistance",
    relationship_changes={
        "char_456": {"affection": 3, "trust": 2}
    }
)
```

## Core Plugin Usage

For direct NPC management operations:

```python
from app.plugins.npc_management_plugin import NPCManagementPlugin

plugin = NPCManagementPlugin()

# Create NPC
result = plugin.create_npc(
    name="Captain Marcus",
    description="A stern guard in polished armor",
    race="human",
    role="guard",
    location="City Gates",
    personality="neutral"
)

# Generate NPC response
response = plugin.generate_npc_response(
    npc_id=npc_id,
    character_id="char_123",
    player_message="State your business here",
    context="Player approaches city gates"
)
```

## Integration with Game Agents

### For Narrator Agents
Use the NPC Integration Service to:
- Create NPCs dynamically during narration
- Get NPCs relevant to current scenes
- Handle player-NPC interactions
- Update NPC states based on story events

### For Scribe Agents
The enhanced Scribe Agent includes NPC management methods:
- `create_npc()` - Create new NPCs
- `get_npc()` - Retrieve NPC details
- `update_npc_relationship()` - Manage relationships
- `get_npcs_in_location()` - Query NPCs by location
- `generate_npc_interaction()` - Handle interactions

### For Dungeon Master Agents
Use the NPC system to:
- Populate locations with appropriate NPCs
- Manage ongoing character-NPC relationships
- Drive plot through NPC interactions
- Maintain narrative consistency

## Data Models

### NPC Model
The core NPC model includes all comprehensive attributes:

```python
class NPC(BaseModel):
    id: str
    name: str
    description: str
    race: Race
    role: NPCRole
    level: int = 1
    
    # Physical attributes
    abilities: Optional[Abilities] = None
    hit_points: Optional[HitPoints] = None
    armor_class: int = 10
    age: Optional[int] = None
    appearance: Optional[str] = None
    
    # Location and status
    current_location: str
    home_location: Optional[str] = None
    is_alive: bool = True
    is_available: bool = True
    
    # Personality and behavior
    personality: NPCPersonality = NPCPersonality.NEUTRAL
    behavior: NPCBehavior = Field(default_factory=NPCBehavior)
    
    # Social connections
    relationships: List[NPCRelationship] = []
    faction: Optional[str] = None
    
    # Memory and knowledge
    memory: NPCMemory = Field(default_factory=NPCMemory)
    languages: List[str] = ["Common"]
    
    # Inventory and economics
    inventory: NPCInventory = Field(default_factory=NPCInventory)
    
    # Quest integration
    available_quests: List[str] = []
    involved_quests: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
```

## Best Practices

### 1. NPC Creation
- Give NPCs distinctive names and detailed descriptions
- Choose appropriate roles and personalities for their location and purpose
- Consider how NPCs fit into the broader narrative

### 2. Interaction Handling
- Use contextual information to generate appropriate responses
- Update relationships based on player actions
- Track important interactions in NPC memory

### 3. Story Integration
- Use NPCs to drive plot points and provide information
- Maintain consistency in NPC behavior and knowledge
- Update NPC states as the story progresses

### 4. Relationship Management
- Gradually build relationships through multiple interactions
- Use relationship changes to reflect player choices
- Consider long-term consequences of relationship dynamics

### 5. Performance Considerations
- Use location-based queries to limit NPC scope
- Clean up NPCs that are no longer relevant to the story
- Consider implementing persistence for long-term campaigns

## Future Enhancements

Potential areas for expansion:

1. **Advanced AI Integration**: Connect with LLMs for more sophisticated dialogue generation
2. **Dynamic Personality**: Allow NPC personalities to evolve based on experiences
3. **Complex Relationships**: Multi-way relationships between NPCs
4. **Economic Simulation**: More sophisticated trading and economic behavior
5. **Quest Generation**: Automatic quest creation based on NPC roles and relationships
6. **Voice and Mannerisms**: Audio and behavioral characteristics for each NPC
7. **Persistence**: Database storage for long-term campaign continuity
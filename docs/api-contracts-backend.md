# API Contracts - Backend

**Generated:** 2025-11-01
**Part:** backend (FastAPI)
**Base URL:** `/` (configurable via API_PREFIX)

## Overview

The backend provides a comprehensive REST API for an AI-powered Dungeons & Dragons game management system, including character creation, campaign management, combat tracking, spell casting, NPC interactions, and real-time WebSocket communication.

## REST API Endpoints

### Character Management

#### POST /character
**Purpose:** Create a new player character
**Request:** `CreateCharacterRequest`
**Response:** `CharacterSheet`
**Status Codes:** 200 OK, 400 Bad Request, 503 Service Unavailable, 500 Internal Server Error

#### GET /character/{character_id}
**Purpose:** Retrieve character details
**Path Params:** `character_id: str`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 404 Not Found

#### POST /character/{character_id}/level-up
**Purpose:** Level up a character
**Path Params:** `character_id: str`
**Request:** `LevelUpRequest`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 400 Bad Request

#### POST /character/{character_id}/apply-level-up
**Purpose:** Apply level up changes to character
**Path Params:** `character_id: str`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK

#### GET /character/{character_id}/progression-info
**Purpose:** Get character progression information
**Path Params:** `character_id: str`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK

### Campaign Management

#### POST /campaign
**Purpose:** Create a new campaign
**Request:** `CreateCampaignRequest`
**Response:** `Campaign`
**Status Codes:** 201 Created, 400 Bad Request, 500 Internal Server Error

#### GET /campaigns
**Purpose:** List all campaigns
**Response:** `CampaignListResponse`
**Status Codes:** 200 OK, 500 Internal Server Error

#### GET /campaign/templates
**Purpose:** Get available campaign templates
**Response:** List of template campaigns
**Status Codes:** 200 OK, 500 Internal Server Error

#### GET /campaign/{campaign_id}
**Purpose:** Get campaign details
**Path Params:** `campaign_id: str`
**Response:** `Campaign`
**Status Codes:** 200 OK, 404 Not Found, 500 Internal Server Error

#### PUT /campaign/{campaign_id}
**Purpose:** Update campaign
**Path Params:** `campaign_id: str`
**Request:** `CampaignUpdateRequest`
**Response:** `Campaign`
**Status Codes:** 200 OK, 404 Not Found, 500 Internal Server Error

#### POST /campaign/clone
**Purpose:** Clone an existing campaign
**Request:** `CloneCampaignRequest`
**Response:** `Campaign`
**Status Codes:** 201 Created, 404 Not Found, 500 Internal Server Error

#### DELETE /campaign/{campaign_id}
**Purpose:** Delete a campaign
**Path Params:** `campaign_id: str`
**Response:** Success message
**Status Codes:** 200 OK, 404 Not Found, 500 Internal Server Error

#### POST /campaign/generate-world
**Purpose:** Generate world content for a campaign
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 400 Bad Request

#### POST /campaign/{campaign_id}/start-session
**Purpose:** Start a new game session
**Path Params:** `campaign_id: str`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 404 Not Found

### AI-Powered Features

#### POST /campaign/ai-assist
**Purpose:** Get AI assistance for campaign planning
**Request:** `AIAssistanceRequest`
**Response:** `AIAssistanceResponse`
**Status Codes:** 200 OK, 400 Bad Request, 503 Service Unavailable

#### POST /campaign/ai-generate
**Purpose:** Generate campaign content using AI
**Request:** `AIContentGenerationRequest`
**Response:** `AIContentGenerationResponse`
**Status Codes:** 200 OK, 400 Bad Request, 503 Service Unavailable

#### POST /generate-image
**Purpose:** Generate images using AI (Artist agent)
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 503 Service Unavailable

#### POST /battle-map
**Purpose:** Generate battle map using Combat Cartographer agent
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 503 Service Unavailable

### Game Session Management

#### POST /input
**Purpose:** Process player input during game session
**Request:** `PlayerInput`
**Response:** `GameResponse`
**Status Codes:** 200 OK, 400 Bad Request, 500 Internal Server Error

#### POST /session/{session_id}/action
**Purpose:** Perform an action during a session
**Path Params:** `session_id: str`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 404 Not Found

### Combat System

#### POST /combat/initialize
**Purpose:** Initialize combat encounter
**Response:** `dict[str, Any]` (includes combat_id, turn_order, initiative rolls)
**Status Codes:** 200 OK, 400 Bad Request

#### POST /combat/{combat_id}/turn
**Purpose:** Execute a combat turn
**Path Params:** `combat_id: str`
**Response:** `dict[str, Any]` (detailed combat results)
**Status Codes:** 200 OK, 404 Not Found

### Spell System

#### POST /character/{character_id}/spells
**Purpose:** Manage character's spell list
**Path Params:** `character_id: str`
**Request:** `ManageSpellsRequest`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 404 Not Found

#### POST /character/{character_id}/spell-slots
**Purpose:** Manage spell slots
**Path Params:** `character_id: str`
**Request:** `ManageSpellSlotsRequest`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 404 Not Found

#### POST /combat/{combat_id}/cast-spell
**Purpose:** Cast a spell during combat
**Path Params:** `combat_id: str`
**Request:** `CastSpellRequest`
**Response:** `SpellCastingResponse`
**Status Codes:** 200 OK, 400 Bad Request

#### GET /spells/list
**Purpose:** Get list of available spells
**Query Params:** Optional filters (class, level, school, etc.)
**Response:** `SpellListResponse`
**Status Codes:** 200 OK

#### POST /spells/save-dc
**Purpose:** Calculate spell save DC
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK

#### POST /spells/concentration-check
**Purpose:** Check concentration on spell
**Request:** `ConcentrationRequest`
**Response:** `ConcentrationCheckResponse`
**Status Codes:** 200 OK

#### POST /spells/attack-bonus
**Purpose:** Calculate spell attack bonus
**Request:** `SpellAttackBonusRequest`
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK

### Equipment & Inventory

#### POST /character/{character_id}/equipment
**Purpose:** Manage character equipment
**Path Params:** `character_id: str`
**Request:** `ManageEquipmentRequest`
**Response:** `EquipmentResponse`
**Status Codes:** 200 OK, 404 Not Found

#### GET /character/{character_id}/encumbrance
**Purpose:** Calculate character encumbrance
**Path Params:** `character_id: str`
**Response:** `EncumbranceResponse`
**Status Codes:** 200 OK, 404 Not Found

#### POST /items/magical-effects
**Purpose:** Get magical item effects
**Request:** `MagicalEffectsRequest`
**Response:** `MagicalEffectsResponse`
**Status Codes:** 200 OK

#### GET /items/catalog
**Purpose:** Get item catalog
**Query Params:** Optional filters (type, rarity, etc.)
**Response:** `ItemCatalogResponse`
**Status Codes:** 200 OK

### Dice Rolling

#### POST /dice/roll
**Purpose:** Roll dice with notation (e.g., "2d6+3")
**Response:** `dict[str, Any]` (includes result, breakdown)
**Status Codes:** 200 OK, 400 Bad Request

#### POST /dice/roll-with-character
**Purpose:** Roll dice with character modifiers
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 400 Bad Request

#### POST /dice/manual-roll
**Purpose:** Submit manual dice roll results
**Response:** `dict[str, Any]`
**Status Codes:** 200 OK, 400 Bad Request

### NPC Management

#### POST /campaign/{campaign_id}/npcs
**Purpose:** Create NPC in campaign
**Path Params:** `campaign_id: str`
**Request:** `CreateNPCRequest`
**Response:** `NPC`
**Status Codes:** 201 Created, 404 Not Found

#### GET /npc/{npc_id}/personality
**Purpose:** Get NPC personality details
**Path Params:** `npc_id: str`
**Response:** `NPCPersonality`
**Status Codes:** 200 OK, 404 Not Found

#### POST /npc/{npc_id}/interaction
**Purpose:** Interact with NPC
**Path Params:** `npc_id: str`
**Request:** `NPCInteractionRequest`
**Response:** `NPCInteractionResponse`
**Status Codes:** 200 OK, 404 Not Found

#### POST /npc/{npc_id}/generate-stats
**Purpose:** Generate NPC stat block
**Path Params:** `npc_id: str`
**Request:** `GenerateNPCStatsRequest`
**Response:** `NPCStatsResponse`
**Status Codes:** 200 OK, 404 Not Found

## WebSocket Endpoints

### Campaign-Specific Chat
**Endpoint:** `/ws/chat/{campaign_id}`
**Purpose:** Real-time chat for specific campaign
**Protocol:** WebSocket
**Authentication:** None (connects on campaign_id)

### Campaign Events
**Endpoint:** `/ws/{campaign_id}`
**Purpose:** Real-time campaign events and updates
**Protocol:** WebSocket
**Authentication:** None

### Global Events
**Endpoint:** `/ws/global`
**Purpose:** Global game events and broadcasts
**Protocol:** WebSocket
**Authentication:** None

## WebSocket Message Types

The WebSocket connections support various message types including:
- **chat_message**: User chat messages
- **chat_input**: Game input during sessions
- **dice_roll**: Dice roll broadcasts
- **game_update**: Game state changes
- **character_update**: Character state changes

## Authentication

Currently, the API does not require authentication. Future implementations may include:
- Session-based authentication
- JWT tokens
- Azure AD integration

## Error Handling

Standard HTTP status codes are used:
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Azure OpenAI service unavailable (fallback mode may be used)

## Rate Limiting

No rate limiting is currently implemented.

## API Versioning

The API does not currently use versioning. All endpoints are at the root level.

## Notes

- Many endpoints rely on Azure AI Agents SDK for intelligent game master functionality
- When Azure OpenAI is unavailable, deterministic fallback logic is used
- All responses use Pydantic models for validation and serialization
- OpenAPI/Swagger documentation available at `/docs`

# Data Models - Backend

**Generated:** 2025-11-01
**Part:** backend (Python + SQLAlchemy)
**Database:** PostgreSQL (production), SQLite (development)
**ORM:** SQLAlchemy 2.0+ (async)
**Migrations:** Alembic

## Overview

The backend uses SQLAlchemy ORM with a hybrid schema approach: structured columns for indexed/queryable fields + JSON columns for flexible data storage. This design balances query performance with schema flexibility for game data.

## Database Tables

### characters

**Purpose:** Stores player character sheets

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String | PRIMARY KEY, INDEXED | Unique character identifier |
| name | String | NOT NULL | Character name |
| data | JSON | NOT NULL | Full character sheet data (abilities, skills, equipment, etc.) |

**Relationships:**
- Referenced by `npc_interactions.character_id` (optional)

**Indexes:**
- Primary key on `id`

**Notes:**
- Flexible JSON schema allows for complex D&D 5e character data
- Character progression, inventory, spell slots all stored in `data` column

---

### campaigns

**Purpose:** Stores campaign settings and world data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String | PRIMARY KEY, INDEXED | Unique campaign identifier |
| name | String | NOT NULL | Campaign name |
| description | Text | NULLABLE | Campaign description |
| setting | Text | NOT NULL | Campaign setting/world |
| tone | String | NOT NULL, DEFAULT='heroic' | Campaign tone (heroic, dark, etc.) |
| homebrew_rules | JSON | NULLABLE, DEFAULT=[] | Custom/house rules |
| world_description | Text | NULLABLE | Generated world lore |
| world_art | JSON | NULLABLE | Generated artwork metadata |
| is_template | Boolean | NOT NULL, DEFAULT=false | Whether campaign is a template |
| is_custom | Boolean | NOT NULL, DEFAULT=true | Whether campaign is custom-created |
| template_id | String | NULLABLE | Source template ID (for clones) |
| created_at | DateTime | NOT NULL, DEFAULT=utcnow() | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT=utcnow(), AUTO-UPDATE | Last update timestamp |
| data | JSON | NOT NULL | Full campaign data (sessions, events, etc.) |

**Relationships:**
- Referenced by `npcs.campaign_id`

**Indexes:**
- Primary key on `id`

**Notes:**
- Template campaigns can be cloned via `template_id` reference
- `world_art` stores references to AI-generated images
- `data` column contains session history, quest tracking, party composition

---

### npcs

**Purpose:** Stores non-player character data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String | PRIMARY KEY, INDEXED | Unique NPC identifier |
| name | String | NOT NULL | NPC name |
| race | String | NULLABLE | NPC race/species |
| occupation | String | NULLABLE | NPC profession |
| location | String | NULLABLE | Current/primary location |
| campaign_id | String | FOREIGN KEY(campaigns.id), NOT NULL | Owning campaign |
| personality | JSON | NOT NULL, DEFAULT={} | Personality traits, motivations |
| stats | JSON | NULLABLE | Stat block (if applicable) |
| relationships | JSON | NOT NULL, DEFAULT=[] | Relationships with PCs/other NPCs |
| created_at | DateTime | NOT NULL, DEFAULT=utcnow() | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT=utcnow(), AUTO-UPDATE | Last update timestamp |
| data | JSON | NOT NULL | Full NPC data |

**Relationships:**
- FOREIGN KEY: `campaign_id` → `campaigns.id`
- Referenced by `npc_interactions.npc_id`

**Indexes:**
- Primary key on `id`
- Foreign key index on `campaign_id`

**Notes:**
- AI-generated NPCs store personality via Azure AI Agents
- `relationships` tracks affinity/hostility with party members
- `stats` contains D&D stat block when NPC is combat-capable

---

### npc_interactions

**Purpose:** Logs all NPC interaction events for history and relationship tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String | PRIMARY KEY, INDEXED | Unique interaction identifier |
| npc_id | String | FOREIGN KEY(npcs.id), NOT NULL | NPC involved |
| character_id | String | FOREIGN KEY(characters.id), NULLABLE | PC involved (if any) |
| interaction_type | String | NOT NULL | Type (dialogue, combat, trade, etc.) |
| summary | Text | NOT NULL | Brief interaction summary |
| outcome | Text | NULLABLE | Outcome description |
| relationship_change | Integer | NOT NULL, DEFAULT=0 | Change in relationship score |
| timestamp | DateTime | NOT NULL, DEFAULT=utcnow() | When interaction occurred |
| data | JSON | NOT NULL | Full interaction details |

**Relationships:**
- FOREIGN KEY: `npc_id` → `npcs.id`
- FOREIGN KEY: `character_id` → `characters.id` (optional)

**Indexes:**
- Primary key on `id`
- Foreign key index on `npc_id`
- Foreign key index on `character_id`

**Notes:**
- Tracks NPC memory and relationship evolution
- Used by AI to maintain conversation continuity
- `relationship_change` affects future NPC behavior

---

### spells

**Purpose:** Stores D&D 5e spell definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | String | PRIMARY KEY, INDEXED | Unique spell identifier |
| name | String | NOT NULL, INDEXED | Spell name |
| level | Integer | NOT NULL | Spell level (0-9) |
| school | String | NOT NULL | School of magic |
| casting_time | String | NOT NULL | Casting time (action, bonus action, etc.) |
| range | String | NOT NULL | Spell range |
| components | JSON | NOT NULL | Components (V, S, M) |
| duration | String | NOT NULL | Duration (instantaneous, concentration, etc.) |
| description | Text | NOT NULL | Spell description |
| higher_levels | Text | NULLABLE | Effects when cast at higher levels |
| ritual | Boolean | NOT NULL, DEFAULT=false | Can be cast as ritual |
| concentration | Boolean | NOT NULL, DEFAULT=false | Requires concentration |
| damage_dice | String | NULLABLE | Damage dice notation (e.g., "2d6") |
| save_type | String | NULLABLE | Saving throw type (STR, DEX, etc.) |
| spell_lists | JSON | NOT NULL, DEFAULT=[] | Classes that can learn spell |
| data | JSON | NOT NULL | Additional spell effects/metadata |

**Indexes:**
- Primary key on `id`
- Index on `name` for fast lookup

**Notes:**
- Populated from D&D 5e SRD data
- `spell_lists` filters spells by character class
- `data` contains detailed mechanical effects for game engine

---

## Database Schema Diagram

```
┌─────────────┐
│  campaigns  │
│             │
│ id (PK)     │───┐
│ name        │   │
│ setting     │   │
│ ...         │   │
└─────────────┘   │
                  │
                  │ campaign_id (FK)
                  │
                  ├─────────────────┐
                  │                 │
                  ▼                 ▼
         ┌─────────────┐   ┌─────────────────┐
         │     npcs    │   │   characters    │
         │             │   │                 │
         │ id (PK)     │   │ id (PK)         │
         │ name        │   │ name            │
         │ personality │   │ data (JSON)     │
         │ campaign_id │   └─────────────────┘
         │ ...         │           │
         └─────────────┘           │
                 │                 │
                 │ npc_id (FK)     │ character_id (FK)
                 │                 │
                 └────────┬────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ npc_interactions │
                 │                  │
                 │ id (PK)          │
                 │ npc_id (FK)      │
                 │ character_id (FK)│
                 │ interaction_type │
                 │ ...              │
                 └──────────────────┘

         ┌─────────────┐
         │   spells    │  (Independent reference table)
         │             │
         │ id (PK)     │
         │ name (IDX)  │
         │ level       │
         │ ...         │
         └─────────────┘
```

## Migration Strategy

**Tool:** Alembic
**Location:** `backend/migrations/versions/`
**Configuration:** `backend/alembic.ini`

### Existing Migrations

1. **9a6d5baf6502_initial_database_schema.py** - Initial schema creation with all 5 tables

### Migration Workflow

1. **Create Migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "description"
   ```

2. **Apply Migration:**
   ```bash
   alembic upgrade head
   ```

3. **Rollback Migration:**
   ```bash
   alembic downgrade -1
   ```

**Auto-Migration:** Migrations run automatically on application startup via `migration_runner.py`

## Data Access Patterns

### Repository Pattern
The application uses service layers (not direct ORM access):
- `app/services/campaign_service.py` - Campaign CRUD operations
- Database access through SQLAlchemy async sessions
- All queries use ORM (no raw SQL)

### Session Management
- Async context managers for database sessions
- Dependency injection via `app/database.py`
- Automatic session cleanup and rollback on errors

## JSON Column Schemas

While JSON columns provide flexibility, the application enforces schemas via Pydantic models:

### characters.data
- Validated by `CharacterSheet` Pydantic model
- Contains: abilities, skills, saving throws, equipment, spell slots, hit points, etc.

### campaigns.data
- Validated by `Campaign` Pydantic model
- Contains: active sessions, quest logs, party roster, world state

### npcs.data
- Validated by `NPC` Pydantic model
- Contains: backstory, quest hooks, inventory, combat tactics

### npc_interactions.data
- Validated by `NPCInteraction` Pydantic model
- Contains: dialogue exchanges, dice rolls, consequences

### spells.data
- Validated by `Spell` Pydantic model
- Contains: spell effects, scaling formulas, restrictions

## Database Configuration

### Environment Variables

```bash
# Production (PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Development (SQLite)
DATABASE_URL=sqlite:///./data/game.db
```

### Connection Pooling
- SQLAlchemy connection pooling enabled
- Pool size configured based on environment

## Performance Considerations

### Indexes
- Primary keys on all `id` columns (automatic)
- Index on `spells.name` for spell lookup
- Foreign key indexes on `campaign_id`, `npc_id`, `character_id`

### Query Optimization
- Eager loading for relationships when needed
- JSON queries use SQLAlchemy JSON operators
- Pagination for list endpoints

### Caching
- No database-level caching currently implemented
- Application-level caching for spell data (in-memory)

## Security

### SQL Injection Prevention
- All queries use SQLAlchemy ORM (parameterized)
- No raw SQL or string concatenation

### Data Validation
- Pydantic models validate all data before database writes
- Foreign key constraints enforce referential integrity

## Future Considerations

### Potential Schema Enhancements
1. **User authentication table** - User accounts, sessions, auth tokens
2. **Party table** - Formalize party relationships between characters and campaigns
3. **Combat encounters table** - Persist combat state across sessions
4. **Dice roll history** - Log all dice rolls for transparency
5. **AI prompt history** - Track AI-generated content for audit

### Optimization Opportunities
1. **Partial indexes** on commonly queried JSON fields
2. **Read replicas** for scaling read-heavy operations
3. **Sharding** by campaign_id for multi-tenant scaling

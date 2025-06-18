# OpenAPI Client Integration

This document describes the integration of a generated TypeScript client from the FastAPI OpenAPI schema.

## Overview

The frontend now uses a generated TypeScript client instead of manually building fetch calls. This eliminates type duplication and ensures the frontend automatically updates when the backend API changes.

## Files Changed

### Generated Client
- `frontend/src/api-client/` - Complete generated client from OpenAPI schema
- `frontend/package.json` - Added `@openapitools/openapi-generator-cli` and npm script

### Updated Files
- `frontend/src/services/api.ts` - Replaced with wrapper around generated client
- Various component files - Updated for stricter TypeScript types

## How It Works

1. **Backend provides OpenAPI schema** at `http://localhost:8000/openapi.json`
2. **Generate client** with `npm run generate:api` 
3. **Wrapper functions** in `api.ts` maintain compatibility with existing frontend code
4. **Type aliases** provide backward compatibility for renamed types

## Type Mappings

The generated API uses different names for some types:

| Frontend (Legacy) | Generated API | 
|-------------------|---------------|
| `Character` | `CharacterSheet` |
| `CharacterCreateRequest` | `CreateCharacterRequest` |
| `CampaignCreateRequest` | `CreateCampaignRequest` |

## Data Structure Changes

### Enums Now Lowercase
- Race: `"Human"` → `"human"`
- CharacterClass: `"Fighter"` → `"fighter"`

### Inventory Structure
- Legacy: `InventoryItem` with `name`, `quantity`
- Generated: `InventorySlot` with `item_id`, `quantity`

## Regenerating the Client

When the backend API changes:

1. Start the backend: `cd backend && python -m app.main`
2. Generate new client: `cd frontend && npm run generate:api`
3. Review any type changes and update wrapper functions if needed

## Benefits

1. **Automatic synchronization** - Frontend types update when backend changes
2. **Type safety** - All API calls are strongly typed
3. **No duplication** - Single source of truth for API types
4. **Documentation** - Generated docs in `src/api-client/docs/`

## Known Issues

1. **Inventory compatibility** - Frontend expects `InventoryItem` but backend provides `InventorySlot`
2. **Optional fields** - Generated types are stricter about nullable fields
3. **Test updates needed** - Some tests need updates for new data formats

## Future Improvements

1. Align backend and frontend inventory data structures
2. Add validation for required fields in components
3. Consider automating client generation in CI/CD pipeline
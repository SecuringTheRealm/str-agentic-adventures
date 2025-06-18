# OpenAPI Client Integration

This document describes the integration of a generated TypeScript client from the FastAPI OpenAPI schema.

## Overview

The frontend now uses a generated TypeScript client instead of manually building fetch calls. This eliminates type duplication and ensures the frontend automatically updates when the backend API changes.

## 🔄 Developer Workflow

**IMPORTANT**: When the backend API changes, developers must regenerate the frontend client to maintain synchronization.

### When to Regenerate the Client

You must regenerate the client when:
- ✅ Adding new API endpoints
- ✅ Modifying existing endpoint parameters or responses
- ✅ Changing data models (request/response types)
- ✅ Updating enum values or field names
- ✅ After pulling backend changes from other developers

### How to Regenerate the Client

1. **Start the backend server:**
   ```bash
   cd backend && python -m app.main
   ```

2. **Regenerate the frontend client:**
   ```bash
   cd frontend && npm run generate:api
   ```

3. **Verify the update:**
   ```bash
   cd frontend && npm run build
   ```

4. **Test the integration:**
   ```bash
   cd frontend && npm test
   ```

### Troubleshooting

If the generation fails:
- Ensure the backend is running on `http://localhost:8000`
- Check that `/openapi.json` endpoint is accessible
- Verify no TypeScript compilation errors in the backend
- Review any API breaking changes that may require frontend updates

### Automated Validation

To validate the entire workflow automatically:
```bash
./scripts/validate-openapi-client.sh
```

This script checks:
- ✅ Backend server accessibility
- ✅ OpenAPI schema validity
- ✅ Client generation success
- ✅ TypeScript compilation

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

⚠️ **This section is deprecated. See the enhanced [Developer Workflow](#-developer-workflow) section above.**

When the backend API changes:

1. Start the backend: `cd backend && python -m app.main`
2. Generate new client: `cd frontend && npm run generate:api`
3. Review any type changes and update wrapper functions if needed

## Benefits

1. **Automatic synchronization** - Frontend types update when backend changes
2. **Type safety** - All API calls are strongly typed
3. **No duplication** - Single source of truth for API types
4. **Documentation** - Generated docs in `src/api-client/docs/`

## 🧪 API Compatibility Testing

To ensure the frontend client stays synchronized with the backend API, automated tests verify:

### Backend Tests (`backend/tests/`)
- `test_api_compatibility.py` - Validates frontend/backend model compatibility
- `test_frontend_backend_integration.py` - Tests endpoint integration
- `test_openapi_schema_validation.py` - Validates OpenAPI schema accessibility

### Frontend Tests
Run the test suite to verify client compatibility:
```bash
cd frontend && npm test
```

### Manual Verification
Test the OpenAPI schema is accessible:
```bash
curl http://localhost:8000/openapi.json
```

## Known Issues

1. **Inventory compatibility** - Frontend expects `InventoryItem` but backend provides `InventorySlot`
2. **Optional fields** - Generated types are stricter about nullable fields
3. **Test updates needed** - Some tests need updates for new data formats

## Future Improvements

1. Align backend and frontend inventory data structures
2. Add validation for required fields in components
3. Consider automating client generation in CI/CD pipeline
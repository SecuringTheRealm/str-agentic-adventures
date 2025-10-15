# Azure OpenAI Requirements

## Overview

This document clarifies which API endpoints and features require Azure OpenAI configuration and which can work without it.

## Endpoints That Work Without Azure OpenAI

These endpoints use basic database operations and don't require AI capabilities:

### Campaign Management
- `POST /api/game/campaign` - Create campaign
- `GET /api/game/campaigns` - List campaigns
- `GET /api/game/campaign/{id}` - Get campaign by ID
- `PUT /api/game/campaign/{id}` - Update campaign
- `DELETE /api/game/campaign/{id}` - Delete campaign
- `GET /api/game/campaign/templates` - Get campaign templates
- `POST /api/game/campaign/clone` - Clone campaign

### Health and Status
- `GET /health` - Health check endpoint
- `GET /openapi.json` - OpenAPI schema

## Endpoints That Require Azure OpenAI

These endpoints use AI agents and require proper Azure OpenAI configuration:

### Character Operations
- `POST /api/game/character` - Create character (uses Scribe agent)
- `GET /api/game/character/{id}` - Get character (may use AI enhancements)

### Image Generation
- `POST /api/game/generate-image` - Generate images (uses Artist agent with DALL-E)

### Gameplay
- `POST /api/game/input` - Process player input (uses Dungeon Master agent)
- WebSocket `/ws/game/{campaign_id}` - Real-time game chat (uses DM agent)

### AI Content Generation
- `POST /api/game/campaign/ai-generate` - AI-assisted content generation

## Configuration Requirements

To enable AI-powered features, set these environment variables:

```bash
AZURE_OPENAI_ENDPOINT=https://your-project.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_DALLE_DEPLOYMENT=dall-e-3  # Optional, for image generation
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

## Error Handling

When Azure OpenAI is not configured, endpoints that require it will return:

```json
{
  "detail": "Azure OpenAI configuration is missing or invalid. This agentic demo requires proper Azure OpenAI setup."
}
```

HTTP Status Code: `503 Service Unavailable`

## Testing Implications

### Unit Tests
- Tests for non-AI endpoints can run without Azure OpenAI configuration
- Tests for AI endpoints should use mocked responses or dependency injection

### Integration Tests
- Use dependency injection to override configuration for testing
- Mock Azure OpenAI client for consistent test results
- See `backend/tests/conftest.py` for fixture examples

### E2E Tests
- E2E tests requiring AI features need actual Azure OpenAI configuration
- Consider splitting E2E tests into:
  - Basic UI/UX tests (no Azure OpenAI needed)
  - AI integration tests (Azure OpenAI required)

## Demo Mode Recommendations

Consider implementing a "demo mode" that:
1. Works without Azure OpenAI for basic testing
2. Uses pre-generated responses for AI features
3. Clearly indicates to users when in demo mode
4. Allows developers to test UI without Azure costs

## Dependency Injection Pattern

If you have existing tests that use environment variable manipulation:

**Old Pattern (Don't Use):**
```python
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = "test"
```

**New Pattern (Use This):**
```python
from app.config import Settings, get_config
from app.main import app

test_config = Settings(
    azure_openai_endpoint="https://test.openai.azure.com",
    azure_openai_api_key="test-key",
    # ... other config
)
app.dependency_overrides[get_config] = lambda: test_config
```

See `backend/tests/conftest.py` for working fixtures and helper utilities that follow this pattern.

## Troubleshooting

### "Azure OpenAI configuration is missing or invalid"

**Symptoms**: Endpoints return 503 errors

**Solutions**:
1. Verify all required environment variables are set
2. Check that endpoint URL includes trailing slash
3. Ensure API key is valid and not expired
4. Verify deployments exist in your Azure OpenAI resource

### Tests Failing Due to Missing Configuration

**Symptoms**: Tests fail with "Azure OpenAI configuration" errors

**Solutions**:
1. Use dependency injection fixtures from `conftest.py`
2. Mock Azure OpenAI client responses
3. Skip tests that require Azure OpenAI in CI environments
4. Use `pytest.mark.skip` for optional AI integration tests

### Azure AI SDK Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'azure.ai.agents'`

**Solutions**:
1. Run `make deps` (or `uv sync`) to install dependencies defined in `pyproject.toml`
2. Confirm `uv` is using the workspace `uv.lock` file (use `uv sync --frozen` in CI)
3. If you previously relied on Semantic Kernel, update imports to use `azure.ai.agents` and `azure.ai.inference`
4. Review `docs/migration-guide-azure-ai-sdk.md` for end-to-end migration examples

## References

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- ADR-0005: Azure OpenAI Integration
- `backend/tests/conftest.py` - Test configuration fixtures
- [Migration Guide: Semantic Kernel to Azure AI Agents SDK](migration-guide-azure-ai-sdk.md)

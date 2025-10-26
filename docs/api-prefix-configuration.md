# API Prefix Configuration

## Overview

The backend API is configured to serve all routes under the `/api` prefix when running in production (Azure Container Apps), while maintaining backward compatibility for local development and testing.

## Environment Detection

The application automatically detects the environment using these environment variables:
- `CONTAINER_APP_NAME` - Set by Azure Container Apps
- `WEBSITE_SITE_NAME` - Set by Azure App Service

When either of these variables is present, the application runs in **production mode** with the `/api` prefix.

## URL Structure

### Production (Azure Container Apps)
All routes are served under the `/api` prefix:
- Health check: `https://{domain}/api/health`
- Campaign templates: `https://{domain}/api/game/campaign/templates`
- Character creation: `https://{domain}/api/game/character`

FastAPI's `root_path` configuration ensures:
1. Routes work with the `/api` prefix for production clients
2. Routes also work without the prefix for backward compatibility
3. OpenAPI/Swagger documentation displays correct URLs

### Development/Testing
Routes are served without the `/api` prefix:
- Health check: `http://localhost:8000/health`
- Campaign templates: `http://localhost:8000/game/campaign/templates`
- Character creation: `http://localhost:8000/game/character`

## Testing

The test suite includes comprehensive coverage for both modes:
- `test_api_prefix_production.py` - Tests production mode with `/api` prefix
- `test_campaign_templates_route_fix.py` - Tests route ordering and endpoints
- All existing tests continue to work in development mode

## Technical Details

The configuration is implemented in `backend/app/main.py`:

```python
# Determine root_path based on environment
# In production (Azure Container Apps), routes are served under /api prefix
# In development/testing, no prefix is used
is_production = bool(
    os.getenv("WEBSITE_SITE_NAME") or os.getenv("CONTAINER_APP_NAME")
)
root_path = "/api" if is_production else ""

app = FastAPI(
    title="AI Dungeon Master API",
    description="Backend API for the AI Dungeon Master application",
    version="0.1.0",
    lifespan=lifespan,
    root_path=root_path,
)
```

## Infrastructure Integration

The Azure infrastructure (`infra/main.bicep`) configures the frontend with:
```bicep
backendUrl: 'https://production-backend.${containerAppsEnvironment.outputs.defaultDomain}/api'
```

This matches the backend's `/api` prefix in production.

## Troubleshooting

### 404 Errors in Production
If you receive 404 errors on API endpoints in production:
1. Verify the `CONTAINER_APP_NAME` environment variable is set
2. Check that requests use the `/api` prefix
3. Review application logs for routing errors

### Routes Not Working Locally
If routes don't work in local development:
1. Ensure you're not setting `CONTAINER_APP_NAME` or `WEBSITE_SITE_NAME` locally
2. Access routes without the `/api` prefix
3. Restart the development server after environment changes

## References
- FastAPI `root_path` documentation: https://fastapi.tiangolo.com/advanced/behind-a-proxy/
- Azure Container Apps environment variables: https://learn.microsoft.com/azure/container-apps/environment-variables

# API Prefix Configuration for Production Deployment

* Status: accepted
* Date: 2025-10-31

## Context and Problem Statement

The production Azure Container Apps deployment expects backend routes to be served under the `/api` prefix (as configured in `infra/main.bicep`), but the FastAPI application was not configured with this prefix. This caused 404 errors when the frontend attempted to access backend endpoints at URLs like `https://production-backend.{domain}/api/game/campaign/templates`.

The challenge was to enable the `/api` prefix in production while maintaining backward compatibility for local development and existing tests that expect routes without the prefix.

## Decision Drivers

* Production infrastructure (Azure Container Apps) expects `/api` prefix based on Bicep configuration
* Must maintain backward compatibility for local development (no prefix)
* Existing test suite must continue to work without modification
* Solution should leverage FastAPI's native capabilities
* Must support both Azure Container Apps and Azure App Service deployments
* No changes should be required to existing route definitions

## Considered Options

* Option 1: Use FastAPI's `root_path` parameter with environment detection
    * Automatically detect production environment via Azure-provided environment variables
    * Configure `root_path="/api"` in production, empty in development
    * Pros: Native FastAPI feature, zero changes to routes, automatic environment detection, maintains full backward compatibility
    * Cons: Relies on environment variables being set correctly

* Option 2: Add explicit `/api` prefix to all route definitions
    * Modify `app.include_router()` calls to add `/api` prefix
    * Pros: Explicit and visible in code
    * Cons: Breaks local development, requires changes to all tests, violates DRY principle

* Option 3: Use a reverse proxy or API gateway
    * Configure Azure to strip/add the `/api` prefix at the infrastructure level
    * Pros: Keeps application code unchanged
    * Cons: More complex infrastructure, harder to test locally, requires infrastructure changes

## Decision Outcome

Chosen option: "Use FastAPI's `root_path` parameter with environment detection"

Justification:
* FastAPI's `root_path` is designed specifically for this use case (serving behind a reverse proxy with path prefix)
* Environment detection is automatic and reliable using Azure-provided variables (`CONTAINER_APP_NAME`, `WEBSITE_SITE_NAME`)
* Zero changes required to existing route definitions
* Full backward compatibility maintained for local development and tests
* Minimal code change (7 lines) with maximum impact
* Follows FastAPI best practices for production deployment

## Consequences

### Positive
* Production routes automatically accessible at expected `/api` prefix
* Local development continues to work unchanged
* All existing tests pass without modification
* OpenAPI/Swagger documentation automatically shows correct URLs in production
* Solution works for both Azure Container Apps and Azure App Service
* Routes work with both prefixed and non-prefixed paths in production (FastAPI handles both)

### Negative
* Depends on Azure environment variables being set correctly
* If environment variables are accidentally set locally, development behavior changes
* Test implementation requires creating new FastAPI instance to validate production behavior

### Risks and Mitigations
* Risk: Environment variables not set in production
  * Mitigation: Azure automatically sets these variables; documented in deployment guide
* Risk: Confusion about which URLs to use
  * Mitigation: Comprehensive documentation added (`docs/adr/0019-api-prefix-configuration.md`)
* Risk: Test complexity
  * Mitigation: Tests create isolated FastAPI instances with explicit root_path configuration

## Implementation Details

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

### Environment Detection

The application automatically detects the environment using these environment variables:
- `CONTAINER_APP_NAME` - Set by Azure Container Apps
- `WEBSITE_SITE_NAME` - Set by Azure App Service

When either of these variables is present, the application runs in **production mode** with the `/api` prefix.

### URL Structure

**Production (Azure Container Apps):**
All routes are served under the `/api` prefix:
- Health check: `https://{domain}/api/health`
- Campaign templates: `https://{domain}/api/game/campaign/templates`
- Character creation: `https://{domain}/api/game/character`

FastAPI's `root_path` configuration ensures:
1. Routes work with the `/api` prefix for production clients
2. Routes also work without the prefix for backward compatibility
3. OpenAPI/Swagger documentation displays correct URLs

**Development/Testing:**
Routes are served without the `/api` prefix:
- Health check: `http://localhost:8000/health`
- Campaign templates: `http://localhost:8000/game/campaign/templates`
- Character creation: `http://localhost:8000/game/character`

### Testing

The test suite includes comprehensive coverage for both modes:
- `test_api_prefix_production.py` - Tests production mode with `/api` prefix
- `test_campaign_templates_route_fix.py` - Tests route ordering and endpoints
- All existing tests continue to work in development mode

### Infrastructure Integration

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

## Links

* Related ADRs: 
  * [ADR-0009](0009-container-app-deployment-strategy.md) - Container App deployment
  * [ADR-0007](0007-github-actions-cicd-pipeline.md) - CI/CD pipeline
* References:
  * [FastAPI Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
  * [Azure Container Apps Environment Variables](https://learn.microsoft.com/azure/container-apps/environment-variables)
* Implementation: `backend/app/main.py`, `backend/tests/test_api_prefix_production.py`

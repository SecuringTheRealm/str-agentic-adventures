# Secure the Realm - Agentic Adventures

AI-powered tabletop RPG application with Python FastAPI backend using Semantic Kernel and TypeScript React frontend. The system uses 6 specialized AI agents to replace a human Dungeon Master while maintaining creativity and D&D 5e SRD compliance.

**ALWAYS follow these instructions first and only fallback to search or bash commands when you encounter unexpected information that does not match what is documented here.**

## Working Effectively

### Prerequisites Installation
- Install UV package manager (modern Python dependency manager):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/home/runner/.local/bin:$PATH"
  ```
- Node.js 18+ is required (package.json specifies 22+ but 20 works with warnings)

### Optimized Copilot Setup Workflow

**IMPORTANT**: The repository includes an optimized GitHub Actions workflow for Copilot agent setup with dependency caching. This workflow is located at `.github/workflows/copilot-setup-steps.yml` and provides:

- **Dependency Caching**: UV Python dependencies cached at `~/.cache/uv` with cache keys based on `pyproject.toml` and `uv.lock` files
- **NPM Caching**: Frontend dependencies cached using `actions/setup-node@v4` built-in caching with `frontend/package-lock.json` as the cache dependency path
- **Performance**: Reduces setup time from 4+ minutes to seconds on cache hits
- **Consistency**: Python 3.12 and Node.js 20 versions aligned with CI workflows
- **Azure Secrets**: Environment variables for Azure services are automatically available for local testing and Playwright E2E tests

The workflow automatically handles:
1. Python and Node.js environment setup
2. Dependency installation with caching (Python via UV, Node.js via npm)
3. Repository checkout for dependency installation
4. Azure secrets exposure for local development and testing (only the secrets configured in the repository are surfaced)

#### Available Azure Environment Variables

The GitHub Actions setup job runs immediately before the Copilot coding agent session starts. Because the coding agent reuses the same runner that executed the workflow, any variables written to the runner environment via `$GITHUB_ENV` become available to the agent automatically.

During the "Propagate configured Azure secrets" step, the workflow writes each configured secret from the list below into the environment. Secrets that are not configured in the repository are skipped, so you can maintain the minimal three-secret configuration without errors while still allowing additional deployments to be surfaced in the future.

Currently configured secrets:

- `AZURE_OPENAI_API_KEY` - Azure AI Foundry API key for OpenAI services
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL (e.g., `https://your-project.openai.azure.com/`)
- `AZURE_OPENAI_CHAT_DEPLOYMENT` - Chat model deployment name (e.g., `gpt-4o-mini`)

Optionally supported secrets (add these in repository settings to expose them to the agent):

- `AZURE_CLIENT_ID` - Application (client) ID from service principal
- `AZURE_OPENAI_API_VERSION` - Azure OpenAI API version for deployed models
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding model deployment name (e.g., `text-embedding-3-large`)
- `AZURE_OPENAI_DALLE_DEPLOYMENT` - Image generation deployment name (e.g., `dall-e-3`)
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_TENANT_ID` - Directory (tenant) ID

These environment variables enable:
- Running backend tests that require Azure OpenAI authentication
- Executing Playwright E2E tests with real Azure services
- Local development with Azure AI Foundry integration
- Testing AI agent functionality without manual environment setup

**Note**: These secrets are automatically masked in GitHub logs to prevent exposure. They are only available when the Copilot agent workflow runs and are not stored in the repository.

For manual setup outside the workflow, follow the steps below.

### Bootstrap, Build, and Test the Repository

1. **Install all dependencies:**
   ```bash
   make deps
   ```
   **TIMING**: Takes ~20 seconds. NEVER CANCEL. Set timeout to 5+ minutes.

2. **Build and start backend server:**
   ```bash
   make run
   ```
   **TIMING**: Server starts in ~2 seconds. NEVER CANCEL. Set timeout to 2+ minutes.
   The backend will be available at http://localhost:8000

3. **Install frontend dependencies (in new terminal):**
   ```bash
   cd frontend
   npm ci --legacy-peer-deps
   ```
   **TIMING**: Takes ~3-4 minutes. NEVER CANCEL. Set timeout to 10+ minutes.

4. **Generate OpenAPI client (CRITICAL for frontend):**
   ```bash
   cd frontend
   npm run generate:api
   ```
   **TIMING**: Takes ~5 seconds. Requires backend server running. Set timeout to 2+ minutes.

5. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```
   **TIMING**: Takes ~10-15 seconds. NEVER CANCEL. Set timeout to 5+ minutes.

6. **Start frontend development server:**
   ```bash
   cd frontend
   npm start
   ```
   **TIMING**: Takes ~15 seconds to ready. NEVER CANCEL. Set timeout to 3+ minutes.
   The frontend will be available at http://localhost:3000

### Run Tests

1. **Backend tests:**
   ```bash
   make test
   ```
   **TIMING**: Takes ~20 seconds. NEVER CANCEL. Set timeout to 10+ minutes.
   **NOTE**: Many tests fail without Azure OpenAI configuration - this is expected in development.

2. **Frontend unit tests:**
   ```bash
   cd frontend
   npm run test:run
   ```
   **TIMING**: Takes ~5 seconds. NEVER CANCEL. Set timeout to 10+ minutes.
   **NOTE**: Tests fail until OpenAPI client is generated.

3. **E2E tests (optional):**
   ```bash
   cd frontend
   npx playwright install  # Install browsers first - takes ~2-5 minutes
   npm run test:e2e
   ```
   **TIMING**: Takes ~3-5 minutes. NEVER CANCEL. Set timeout to 15+ minutes.

### Linting and Formatting

1. **Format code (always run first):**
   ```bash
   make format
   ```
   **TIMING**: Takes <1 second. Set timeout to 2+ minutes.

2. **Check linting:**
   ```bash
   make lint
   ```
   **TIMING**: Takes <1 second. Set timeout to 2+ minutes.
   **NOTE**: Project has many linting issues - focus only on new code.

3. **Frontend linting (uses Biome):**
   ```bash
   cd frontend
   npx biome check .
   ```

## Validation

### Manual Testing Requirements
- **ALWAYS run through complete user scenarios after making changes.**
- Test the full workflow: Campaign Creation → Character Creation → Gameplay
- Verify both backend API endpoints and frontend UI work together
- Check OpenAPI client generation workflow when backend APIs change

### Key User Scenarios to Test:
1. **Campaign Creation Flow:**
   - Navigate to http://localhost:3000
   - Click "Create New Campaign"
   - Fill out campaign details
   - Verify campaign is created and listed

2. **Character Creation Flow:**
   - Select an existing campaign
   - Create a new D&D 5e character
   - Verify character sheet displays correctly

3. **API Integration Testing:**
   - Test backend health endpoint: `curl http://localhost:8000/health`
   - Verify OpenAPI schema: `curl http://localhost:8000/openapi.json`
   - Confirm frontend can communicate with backend

### Critical Validation Steps
- **ALWAYS regenerate the OpenAPI client after backend API changes:**
  ```bash
  cd frontend && npm run generate:api
  ```
- **ALWAYS test the complete build process before submitting:**
  ```bash
  make deps && make run &
  cd frontend && npm ci --legacy-peer-deps && npm run generate:api && npm run build
  ```
- **ALWAYS run formatting before committing or the CI will fail:**
  ```bash
  make format
  ```

## Repository Structure

### Backend (`backend/`)
- **Technology**: Python 3.12+ with FastAPI, UV package manager, Semantic Kernel
- **Key Files**:
  - `app/main.py` - FastAPI application entry point
  - `app/agents/` - Six specialized AI agents (DM, Narrator, Scribe, Combat MC, Cartographer, Artist)
  - `app/api/` - API route definitions
  - `app/models/` - Pydantic data models
  - `tests/` - Pytest test suite with factories

### Frontend (`frontend/`)
- **Technology**: TypeScript + React with Material-UI
- **Key Files**:
  - `src/components/` - React components
  - `src/api-client/` - Generated OpenAPI TypeScript client (DO NOT EDIT MANUALLY)
  - `src/services/` - API service layer
  - `e2e/` - Playwright end-to-end tests

### Build System
- **Backend**: Makefile + UV package manager for standardized commands
- **Frontend**: Standard npm scripts
- **CI/CD**: Multiple GitHub workflows (unit tests, integration tests, E2E tests)
- **Copilot Setup**: Optimized workflow with dependency caching at `.github/workflows/copilot-setup-steps.yml`

## Environment Configuration

### Azure OpenAI Setup (Optional for Development)
For full functionality, create `backend/.env`:
```env
AZURE_OPENAI_ENDPOINT=https://your-project.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Known Issues and Workarounds
1. **Node.js Version Warning**: Package.json requires Node 22+, but Node 20 works with warnings
2. **UV Not Found**: Install UV using the curl command in prerequisites
3. **OpenAPI Client Missing**: Always run `npm run generate:api` after backend changes
4. **Test Failures**: Many tests fail without Azure OpenAI configuration - this is expected
5. **Validation Script**: `scripts/validate-openapi-client.sh` expects requirements.txt but project uses UV

## Common Commands Reference

| Command | Purpose | Timing | Directory |
|---------|---------|---------|-----------|
| `make deps` | Install backend dependencies | ~20s | Root |
| `make run` | Start backend server | ~2s startup | Root |
| `make test` | Run backend tests | ~20s | Root |
| `make lint` | Check code linting | <1s | Root |
| `make format` | Format code | <1s | Root |
| `npm ci --legacy-peer-deps` | Install frontend deps | ~3-4min | frontend/ |
| `npm run build` | Build frontend | ~10-15s | frontend/ |
| `npm start` | Start frontend dev server | ~15s | frontend/ |
| `npm run generate:api` | Generate OpenAPI client | ~5s | frontend/ |
| `npm run test:run` | Run frontend tests | ~5s | frontend/ |
| `npm run test:e2e` | Run E2E tests | ~3-5min | frontend/ |

## Development Workflow

1. **Starting Development:**
   ```bash
   make deps && make run &  # Start backend
   cd frontend && npm ci --legacy-peer-deps && npm run generate:api && npm start
   ```

2. **After Backend API Changes:**
   ```bash
   cd frontend && npm run generate:api && npm run build
   ```

3. **Before Committing:**
   ```bash
   make format && make lint  # Check backend
   cd frontend && npx biome check .  # Check frontend
   ```

4. **Full Validation:**
   ```bash
   make test  # Backend tests
   cd frontend && npm run test:run && npm run build  # Frontend tests and build
   ```

## Architecture Notes

- **Multi-Agent System**: 6 specialized AI agents work together for tabletop RPG experience
- **D&D 5e SRD Compliance**: All game mechanics follow D&D 5e System Reference Document
- **Real-time Features**: FastAPI backend with React frontend for immediate responses
- **OpenAPI Integration**: Frontend TypeScript client is auto-generated from backend schema
- **Modern Python**: Uses UV package manager for faster, reproducible builds
- **Testing Strategy**: Unit tests, integration tests, and E2E tests with Playwright

## Project Documentation

For comprehensive project documentation, refer to `docs/`:

- **[Azure OpenAI Requirements](docs/AZURE_OPENAI_REQUIREMENTS.md)** - Which endpoints require Azure OpenAI, configuration guide, and testing implications
- **[Testing Strategy](docs/specs/TESTING_STRATEGY.md)** - Testing best practices, patterns, coverage requirements, and troubleshooting
- **[E2E Test Summary](docs/specs/E2E_TEST_SUMMARY.md)** - End-to-end testing results and improvements
- **[Agent Documentation](AGENTS.md)** - Detailed information about the AI agents

**Note for AI Agents**: When creating new documentation files in the `docs/` directory, add references to them in this section of `.github/copilot-instructions.md` and in the corresponding section of `AGENTS.md`. When removing documentation files, remove their references from both files.

**Remember**: This is a working application that requires both backend and frontend to be running for complete functionality. Always validate your changes with manual testing of the user workflows.

Review the appropriate coding instructions in .github/instructions/ 

# Scripts Directory

This directory contains utility scripts for development, testing, and validation.

## Available Scripts

### test-azure-secrets.sh

Tests whether Azure OpenAI secrets are properly configured and available in the environment.

**Purpose**: Validates that the GitHub Copilot coding agent has access to required Azure OpenAI secrets.

**Usage**:
```bash
bash scripts/test-azure-secrets.sh
```

**What it checks**:

**Required secrets** (must be present for basic functionality):
- `AZURE_OPENAI_API_KEY` - Azure AI Foundry API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_CHAT_DEPLOYMENT` - Chat model deployment name

**Optional secrets** (for additional features):
- `AZURE_CLIENT_ID` - Service principal client ID
- `AZURE_OPENAI_API_VERSION` - API version override
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding model name
- `AZURE_OPENAI_DALLE_DEPLOYMENT` - DALL-E model name
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_TENANT_ID` - Azure tenant ID

**Exit codes**:
- `0` - All required secrets are configured
- `1` - One or more required secrets are missing

**Troubleshooting**: If the test fails, see [`docs/copilot-secrets-troubleshooting.md`](../docs/copilot-secrets-troubleshooting.md).

### validate-openapi-client.sh

Validates that the frontend OpenAPI client is properly generated and synchronized with the backend API.

**Purpose**: Ensures the generated API client matches the backend OpenAPI schema.

**Usage**:
```bash
bash scripts/validate-openapi-client.sh
```

**Prerequisites**:
- Backend server must be running on `http://localhost:8000`
- Frontend dependencies must be installed

**What it checks**:
- Backend OpenAPI schema is accessible
- Generated client files exist in `frontend/src/api-client/`
- Client is up-to-date with current backend schema

**When to run**:
- After making changes to backend API endpoints
- After updating request/response models
- Before committing frontend changes

**Troubleshooting**: If validation fails, regenerate the client:
```bash
cd frontend
npm run generate:api
```

## Development Workflow

### Setting Up Development Environment

1. **Verify Azure secrets** (for Copilot agent and local testing):
   ```bash
   bash scripts/test-azure-secrets.sh
   ```

2. **Install dependencies**:
   ```bash
   make deps
   ```

3. **Start backend server**:
   ```bash
   make run
   ```

4. **Generate OpenAPI client** (in new terminal):
   ```bash
   cd frontend
   npm run generate:api
   ```

5. **Validate API client**:
   ```bash
   bash scripts/validate-openapi-client.sh
   ```

6. **Start frontend** (in new terminal):
   ```bash
   cd frontend
   npm start
   ```

### Before Committing Changes

1. **Run formatters and linters**:
   ```bash
   make format
   make lint
   ```

2. **Run tests**:
   ```bash
   make test                    # Backend tests
   cd frontend && npm run test:run  # Frontend tests
   ```

3. **Validate API sync** (if backend changes):
   ```bash
   bash scripts/validate-openapi-client.sh
   ```

## Adding New Scripts

When adding new scripts to this directory:

1. **Use descriptive names** following the pattern `<verb>-<noun>.sh`
2. **Make scripts executable**: `chmod +x scripts/your-script.sh`
3. **Add usage documentation** to this README
4. **Include error handling** with proper exit codes
5. **Add colored output** for better readability (see test-azure-secrets.sh for examples)
6. **Test scripts** in both local and CI environments

## Script Best Practices

### Shell Script Standards

- Use `#!/bin/bash` shebang
- Add `set -euo pipefail` for safety
- Include usage help with `-h` or `--help` flag
- Return proper exit codes (0 for success, non-zero for failure)
- Use colored output for important messages

### Colored Output Functions

Example from test-azure-secrets.sh:

```bash
print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}
```

### Testing Scripts

Test scripts in multiple environments:

1. **Local development**: `bash scripts/your-script.sh`
2. **CI environment**: Add to `.github/workflows/` if appropriate
3. **Error cases**: Test with missing dependencies, wrong permissions, etc.

## Getting Help

- **Documentation issues**: Check `docs/` directory
- **CI/CD issues**: Check `.github/workflows/` directory
- **General help**: See [README.md](../README.md)

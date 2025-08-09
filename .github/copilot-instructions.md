# Securing the Realm - Agentic Adventures

AI-powered web application for tabletop RPGs with Python backend (FastAPI + Semantic Kernel) and TypeScript/React frontend. The platform uses specialized AI agents to replace the human Dungeon Master while maintaining creativity and immersion.

**ALWAYS** reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Prerequisites and Environment Setup
- **Python 3.12+** for backend (verified working: Python 3.12.3)
- **Node.js 20+** for frontend (WARNING: package.json requires >=22.0.0 but works with 20.19.4)
- **Azure OpenAI access** required for full functionality (optional for basic development)

### Bootstrap, Build, and Test the Repository

#### Backend Setup (Python)
```bash
cd backend

# Option 1: Using pip (TESTED - WORKS)
pip install -r requirements.txt
# Takes 1-2 minutes for initial install

# Option 2: Using start.sh script (FALLBACK - UV install may fail in some environments)
./start.sh
# NOTE: May fail to install UV but will fall back to using existing Python/pip

# Start backend server
python -m app.main
# Server starts on http://0.0.0.0:8000
# TESTED: Starts successfully even without Azure OpenAI configuration
```

#### Frontend Setup (TypeScript/React)
```bash
cd frontend

# Install dependencies
npm install
# Takes 3-4 minutes for initial install
# IGNORE: Node.js version warnings and deprecation warnings

# Build frontend
npm run build
# Takes 10-15 seconds. NEVER CANCEL. Set timeout to 60+ seconds for safety.
```

#### Essential OpenAPI Client Generation Workflow
**CRITICAL**: When backend API changes, regenerate the frontend client:

```bash
# 1. Start backend server (in terminal 1)
cd backend && python -m app.main

# 2. Generate frontend client (in terminal 2)
cd frontend && npm run generate:api
# Takes 5-10 seconds. Requires backend running on http://localhost:8000

# 3. Verify build still works
npm run build
```

### Running the Application

#### Development Mode
```bash
# Terminal 1: Backend
cd backend
python -m app.main
# Runs on http://localhost:8000

# Terminal 2: Frontend  
cd frontend
npm start
# Runs on http://localhost:3000
# Takes 30-60 seconds to start. NEVER CANCEL.
```

#### Production Build
```bash
cd frontend
npm run build
# Creates optimized build in frontend/build/
```

### Testing

#### Backend Tests
```bash
cd backend

# Syntax validation (TESTED - WORKS)
python -c "
import ast, os
python_files = []
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))
for file_path in python_files:
    with open(file_path, 'r') as f:
        ast.parse(f.read())
    print(f'✅ {file_path} syntax valid')
print('✅ All Python files valid')
"

# Full test suite (NOTE: Currently has pytest config issues)
python -m pytest tests/ -x --tb=short
# May fail due to asyncio_mode config - use syntax validation instead
```

#### Frontend Tests
```bash
cd frontend

# Unit tests
npm test -- --run
# Takes 5-10 seconds

# NOTE: Tests will fail if OpenAPI client is not generated
# Run OpenAPI generation workflow first if tests fail
```

#### End-to-End Validation
```bash
# Comprehensive validation script (TESTED - WORKS)
./scripts/validate-openapi-client.sh
# Takes 20-30 seconds. NEVER CANCEL. Set timeout to 60+ seconds.
# Validates: backend startup, OpenAPI schema, client generation, TypeScript compilation
```

## Validation

### Manual Application Testing
After making changes, **ALWAYS** run through this validation scenario:

1. **Start both backend and frontend**:
   ```bash
   # Terminal 1
   cd backend && python -m app.main
   
   # Terminal 2  
   cd frontend && npm start
   ```

2. **Verify application loads**: Navigate to http://localhost:3000
   - Should see "Securing the Realm - Agentic Adventures" header
   - Should see "Campaign Hub" section
   - Should see "Gallery" and "My Campaigns" buttons
   - API errors are expected without Azure OpenAI configuration

3. **Test backend health**: `curl http://localhost:8000/health`
   - Should return: `{"status":"ok","version":"0.1.0"}`

4. **Verify OpenAPI schema**: `curl http://localhost:8000/openapi.json | head -5`
   - Should return valid JSON schema

### Always Run Before Committing
```bash
# Backend validation
cd backend && python -c "import ast, os; [ast.parse(open(f).read()) for f in [os.path.join(r,f) for r,d,files in os.walk('app') for f in files if f.endswith('.py')]]"

# Frontend validation  
cd frontend && npm run build

# Full integration test
./scripts/validate-openapi-client.sh
```

## Common Tasks

### Repository Structure
```
/home/runner/work/str-agentic-adventures/str-agentic-adventures/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Main application code
│   ├── tests/              # Test suite
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml     # Project configuration
│   └── start.sh           # Startup script (UV + fallback)
├── frontend/               # TypeScript React frontend
│   ├── src/               # Source code
│   ├── src/api-client/    # Generated OpenAPI client (DO NOT EDIT)
│   ├── package.json       # Node dependencies
│   └── public/            # Static assets
├── scripts/               # Utility scripts
│   └── validate-openapi-client.sh  # Full validation
├── docs/                  # Documentation
└── .github/              # GitHub workflows and instructions
```

### Key Technologies
- **Backend**: Python 3.12, FastAPI, Semantic Kernel, Azure OpenAI, SQLAlchemy
- **Frontend**: TypeScript, React 19, Material-UI, Axios, Vitest (testing)
- **Build Tools**: npm, pip/uv, OpenAPI Generator
- **Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)

### Azure OpenAI Setup (Optional)
For full functionality, create `.env` file in `backend/`:
```bash
# Copy from backend/.env.example
AZURE_OPENAI_ENDPOINT=https://your-project.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Important Commands Reference
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend dev server check  
curl http://localhost:3000

# OpenAPI schema check
curl http://localhost:8000/openapi.json

# Full validation workflow
./scripts/validate-openapi-client.sh

# Quick syntax check
cd backend && python -m py_compile app/main.py
```

### Troubleshooting

**Backend won't start**: Check Python version `python --version` (need 3.12+)

**Frontend build fails**: 
1. Check Node version `node --version` (need 20+)
2. Try `rm -rf node_modules package-lock.json && npm install`

**OpenAPI client errors**: 
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Regenerate client: `cd frontend && npm run generate:api`
3. Rebuild: `npm run build`

**Tests fail**: 
1. Backend: Use syntax validation instead of pytest
2. Frontend: Generate OpenAPI client first, then run tests

## Timing Expectations

- **Backend dependency install**: 1-2 minutes
- **Frontend dependency install**: 3-4 minutes  
- **Backend startup**: 5-10 seconds
- **Frontend dev server startup**: 30-60 seconds
- **Frontend build**: 10-15 seconds
- **OpenAPI client generation**: 5-10 seconds
- **Full validation script**: 20-30 seconds

**NEVER CANCEL**: All build and startup commands. Set timeouts to at least 2x expected time.

---

Review the appropriate coding instructions in .github/instructions/ 

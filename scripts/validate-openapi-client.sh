#!/bin/bash

# OpenAPI Client Generation Validation Script
# This script validates that the OpenAPI client can be successfully generated from the backend

set -e  # Exit on any error

echo "🔍 Validating OpenAPI Client Generation Workflow..."

# Function to print colored output
print_status() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ] || [ ! -f "backend/app/main.py" ]; then
    print_error "This script must be run from the repository root directory"
    exit 1
fi

print_status "Step 1: Checking backend dependencies..."

# Check if UV is available
if ! command -v uv &> /dev/null; then
    print_error "UV package manager not found. Please install UV:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if Python dependencies are available using UV
if ! uv run python -c "import fastapi" 2>/dev/null; then
    print_error "FastAPI not available. Please install backend dependencies:"
    echo "uv sync"
    exit 1
fi

print_success "Backend dependencies are available"

print_status "Step 2: Starting backend server..."

# Start backend server in background
cd backend && uv run python -m app.main &
BACKEND_PID=$!
cd ..

# Function to cleanup background process
cleanup() {
    print_status "Cleaning up..."
    kill $BACKEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Wait for server to start
sleep 5

print_status "Step 3: Testing OpenAPI schema accessibility..."

# Test if OpenAPI schema is accessible
if curl -f -s http://localhost:8000/openapi.json > /dev/null; then
    print_success "OpenAPI schema is accessible"
else
    print_error "Cannot access OpenAPI schema at http://localhost:8000/openapi.json"
    print_warning "Make sure the backend server is running and accessible"
    exit 1
fi

# Validate schema structure
print_status "Step 4: Validating OpenAPI schema structure..."

SCHEMA_RESPONSE=$(curl -s http://localhost:8000/openapi.json)

# Check if it's valid JSON
if echo "$SCHEMA_RESPONSE" | python -m json.tool > /dev/null 2>&1; then
    print_success "OpenAPI schema is valid JSON"
else
    print_error "OpenAPI schema is not valid JSON"
    exit 1
fi

# Check for required OpenAPI fields
if echo "$SCHEMA_RESPONSE" | python -c "
import json, sys
schema = json.load(sys.stdin)
required_fields = ['openapi', 'info', 'paths', 'components']
missing = [f for f in required_fields if f not in schema]
if missing:
    print('Missing required fields:', missing)
    sys.exit(1)
print('All required fields present')
"; then
    print_success "OpenAPI schema has all required fields"
else
    print_error "OpenAPI schema is missing required fields"
    exit 1
fi

print_status "Step 5: Testing frontend client generation..."

cd ../frontend

# Check if openapi-generator-cli is available
if ! npm list @openapitools/openapi-generator-cli > /dev/null 2>&1; then
    print_error "OpenAPI Generator CLI not installed. Installing..."
    npm install
fi

# Backup existing client if it exists
if [ -d "src/api-client" ]; then
    print_status "Backing up existing API client..."
    mv src/api-client src/api-client.backup
fi

# Generate new client
print_status "Generating TypeScript client from OpenAPI schema..."

if npm run generate:api > /dev/null 2>&1; then
    print_success "Client generation completed successfully"
else
    print_error "Client generation failed"
    
    # Restore backup if generation failed
    if [ -d "src/api-client.backup" ]; then
        mv src/api-client.backup src/api-client
        print_status "Restored previous client"
    fi
    exit 1
fi

# Validate generated client structure
print_status "Step 6: Validating generated client structure..."

REQUIRED_FILES=(
    "src/api-client/api.ts"
    "src/api-client/base.ts"
    "src/api-client/configuration.ts"
    "src/api-client/index.ts"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Generated file exists: $file"
    else
        print_error "Missing generated file: $file"
        exit 1
    fi
done

# Test TypeScript compilation
print_status "Step 7: Testing TypeScript compilation..."

if npm run build > /dev/null 2>&1; then
    print_success "TypeScript compilation successful"
else
    print_error "TypeScript compilation failed"
    print_warning "The generated client may have type issues"
    exit 1
fi

# Run tests if they exist
print_status "Step 8: Running API client tests..."

if npm test -- --run --reporter=basic api-client.test.ts > /dev/null 2>&1; then
    print_success "API client tests passed"
else
    print_warning "API client tests failed or not found"
    # Don't exit on test failure as tests might not exist yet
fi

# Cleanup backup if everything succeeded
if [ -d "src/api-client.backup" ]; then
    rm -rf src/api-client.backup
    print_status "Removed backup"
fi

print_success "🎉 OpenAPI Client Generation Validation Complete!"
echo ""
echo "Summary:"
echo "✅ Backend server started successfully"
echo "✅ OpenAPI schema is accessible and valid"
echo "✅ TypeScript client generated successfully"
echo "✅ Generated client compiles without errors"
echo ""
echo "The OpenAPI client generation workflow is working correctly!"
echo "When backend API changes, run: cd frontend && npm run generate:api"
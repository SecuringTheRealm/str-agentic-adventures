#!/bin/bash

# Azure Secrets Testing Script
# This script verifies that Azure OpenAI secrets are properly propagated to the Copilot agent environment

set -euo pipefail

echo "🔍 Testing Azure OpenAI Secret Propagation..."
echo ""

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

# Track test results
REQUIRED_SECRETS_MISSING=0
OPTIONAL_SECRETS_MISSING=0
REQUIRED_SECRETS_FOUND=0
OPTIONAL_SECRETS_FOUND=0

echo "Testing Required Azure Secrets:"
echo "================================"
echo ""

# Test required secrets (minimal configuration for basic functionality)
REQUIRED_VARS=(
    "AZURE_OPENAI_API_KEY"
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_CHAT_DEPLOYMENT"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var:-}" ]; then
        print_success "$var is set"
        REQUIRED_SECRETS_FOUND=$((REQUIRED_SECRETS_FOUND + 1))
    else
        print_error "$var is NOT set (required)"
        REQUIRED_SECRETS_MISSING=$((REQUIRED_SECRETS_MISSING + 1))
    fi
done

echo ""
echo "Testing Optional Azure Secrets:"
echo "================================"
echo ""

# Test optional secrets (for additional features)
OPTIONAL_VARS=(
    "AZURE_CLIENT_ID"
    "AZURE_OPENAI_API_VERSION"
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    "AZURE_OPENAI_DALLE_DEPLOYMENT"
    "AZURE_SUBSCRIPTION_ID"
    "AZURE_TENANT_ID"
)

for var in "${OPTIONAL_VARS[@]}"; do
    if [ -n "${!var:-}" ]; then
        print_success "$var is set"
        OPTIONAL_SECRETS_FOUND=$((OPTIONAL_SECRETS_FOUND + 1))
    else
        print_warning "$var is NOT set (optional)"
        OPTIONAL_SECRETS_MISSING=$((OPTIONAL_SECRETS_MISSING + 1))
    fi
done

echo ""
echo "Summary:"
echo "========"
echo ""
echo "Required secrets: $REQUIRED_SECRETS_FOUND/${#REQUIRED_VARS[@]} configured"
echo "Optional secrets: $OPTIONAL_SECRETS_FOUND/${#OPTIONAL_VARS[@]} configured"
echo ""

# Exit with failure if required secrets are missing
if [ $REQUIRED_SECRETS_MISSING -gt 0 ]; then
    print_error "Test FAILED: $REQUIRED_SECRETS_MISSING required secret(s) missing"
    echo ""
    echo "The following secrets must be configured in GitHub repository settings:"
    echo "- AZURE_OPENAI_API_KEY"
    echo "- AZURE_OPENAI_ENDPOINT" 
    echo "- AZURE_OPENAI_CHAT_DEPLOYMENT"
    echo ""
    echo "See docs/deployment.md for configuration instructions."
    exit 1
else
    print_success "Test PASSED: All required secrets are configured"
    echo ""
    if [ $OPTIONAL_SECRETS_MISSING -gt 0 ]; then
        print_warning "Note: $OPTIONAL_SECRETS_MISSING optional secret(s) not configured (this is okay)"
    fi
    exit 0
fi

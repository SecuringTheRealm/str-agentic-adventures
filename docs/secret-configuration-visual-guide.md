# Secret Configuration Issue - Visual Guide

## Current State (Problem) ❌

```
GitHub Repository Settings
│
├─ Secrets and variables
│   ├─ Actions
│   │   └─ Repository secrets
│   │       ├─ AZURE_OPENAI_ENDPOINT ✅
│   │       ├─ AZURE_OPENAI_CHAT_DEPLOYMENT ✅
│   │       ├─ AZURE_CLIENT_ID ✅
│   │       └─ ... (other secrets) ✅
│   │
│   └─ Copilot
│       └─ Copilot-specific secrets
│           └─ AZURE_OPENAI_API_KEY ❌
│               (Not accessible to workflows!)
│
↓
│
GitHub Actions Workflow (.github/workflows/copilot-setup-steps.yml)
│
├─ Step: Propagate configured Azure secrets
│   env:
│     AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
│                            └─ Returns EMPTY! ❌
│     AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
│                            └─ Returns value ✅
│
└─ Writes to $GITHUB_ENV:
    ├─ AZURE_OPENAI_ENDPOINT=https://... ✅
    ├─ AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini ✅
    └─ (AZURE_OPENAI_API_KEY skipped - empty value) ❌
│
↓
│
Copilot Agent Environment
│
├─ Environment Variables:
│   ├─ AZURE_OPENAI_ENDPOINT ✅
│   ├─ AZURE_OPENAI_CHAT_DEPLOYMENT ✅
│   └─ AZURE_OPENAI_API_KEY ❌ (NOT SET!)
│
└─ Special Copilot Variables:
    └─ COPILOT_AGENT_INJECTED_SECRET_NAMES=AZURE_OPENAI_API_KEY
       (Name is known, but value is not accessible)
│
↓
│
Backend Application
│
└─ Cannot authenticate with Azure OpenAI ❌
    (Missing API key)
```

## Fixed State (Solution) ✅

```
GitHub Repository Settings
│
├─ Secrets and variables
│   ├─ Actions
│   │   └─ Repository secrets
│   │       ├─ AZURE_OPENAI_API_KEY ✅ (MOVED HERE!)
│   │       ├─ AZURE_OPENAI_ENDPOINT ✅
│   │       ├─ AZURE_OPENAI_CHAT_DEPLOYMENT ✅
│   │       ├─ AZURE_CLIENT_ID ✅
│   │       └─ ... (other secrets) ✅
│   │
│   └─ Copilot
│       └─ Copilot-specific secrets
│           └─ (empty - not used)
│
↓
│
GitHub Actions Workflow (.github/workflows/copilot-setup-steps.yml)
│
├─ Step: Propagate configured Azure secrets
│   env:
│     AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
│                            └─ Returns value! ✅
│     AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
│                            └─ Returns value ✅
│
└─ Writes to $GITHUB_ENV:
    ├─ AZURE_OPENAI_API_KEY=sk-... ✅
    ├─ AZURE_OPENAI_ENDPOINT=https://... ✅
    └─ AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini ✅
│
↓
│
Copilot Agent Environment
│
└─ Environment Variables:
    ├─ AZURE_OPENAI_API_KEY ✅ (NOW AVAILABLE!)
    ├─ AZURE_OPENAI_ENDPOINT ✅
    └─ AZURE_OPENAI_CHAT_DEPLOYMENT ✅
│
↓
│
Backend Application
│
└─ Successfully authenticates with Azure OpenAI ✅
    └─ All AI features work! ✅
```

## Key Difference

### Wrong Configuration (Current) ❌
- Secret is in: **Copilot > Copilot-specific secrets**
- Accessible in workflows: **NO** ❌
- Accessible to agent: **NO** ❌

### Correct Configuration (Required) ✅
- Secret is in: **Actions > Repository secrets**
- Accessible in workflows: **YES** ✅
- Accessible to agent: **YES** ✅

## How to Fix

### Step 1: Access Repository Settings
1. Go to your GitHub repository
2. Click **Settings** (top right)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions** (NOT Copilot)

### Step 2: Add Secret as Repository Secret
1. Under **Repository secrets**, click **New repository secret**
2. Name: `AZURE_OPENAI_API_KEY`
3. Value: Your Azure AI Foundry API key
   - Get from [ai.azure.com](https://ai.azure.com)
   - Project Settings > Keys & Endpoint
4. Click **Add secret**

### Step 3: Remove from Copilot Secrets (if present)
1. Click **Secrets and variables** > **Copilot**
2. If `AZURE_OPENAI_API_KEY` is listed, delete it
3. This ensures no confusion about secret location

### Step 4: Verify
1. Start a new Copilot agent session
2. Run: `bash scripts/test-azure-secrets.sh`
3. Should show: `✅ AZURE_OPENAI_API_KEY is set`

## Testing Commands

```bash
# Test secret availability
bash scripts/test-azure-secrets.sh

# Expected output after fix:
# ✅ AZURE_OPENAI_API_KEY is set
# ✅ AZURE_OPENAI_ENDPOINT is set
# ✅ AZURE_OPENAI_CHAT_DEPLOYMENT is set
# ✅ Test PASSED: All required secrets are configured
```

## Documentation References

- **Full troubleshooting guide**: [`copilot-secrets-troubleshooting.md`](./copilot-secrets-troubleshooting.md)
- **Testing results**: [`azure-secret-testing-results.md`](./azure-secret-testing-results.md)
- **Deployment guide**: [`deployment.md`](./deployment.md)
- **Scripts documentation**: [`../scripts/README.md`](../scripts/README.md)

## Quick Reference

| Aspect | Copilot-Specific Secret | Repository Secret |
|--------|------------------------|-------------------|
| Location | Secrets > Copilot | Secrets > Actions |
| Workflow Access | ❌ No | ✅ Yes |
| Agent Access | ❌ No | ✅ Yes |
| Use Case | (Not recommended) | ✅ **Use this!** |

# Azure AI Foundry Dev Deployment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy a fresh dev environment to the MVP tenant using Azure AI Foundry with broad model support (OpenAI + Phi-4 + Llama-4), then test until everything works end-to-end.

**Architecture:** Add an `ai-foundry.bicep` module that provisions an AIServices resource with 5 model deployments. Update `main.bicep` to wire it in, update backend config defaults, and deploy via `azd up`. The existing `AsyncAzureOpenAI` client is compatible with Foundry endpoints — no SDK changes needed.

**Tech Stack:** Bicep IaC, Azure AI Foundry (`kind: AIServices`), azd CLI, Python/FastAPI backend, React/Vite frontend, Playwright E2E tests

---

### Task 1: Create AI Foundry Bicep Module

**Files:**
- Create: `infra/modules/ai-foundry.bicep`

- [ ] **Step 1: Write the Foundry module**

```bicep
@description('Name of the AI Foundry resource')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

@description('Whether to disable local (key-based) auth')
param disableLocalAuth bool = false

@description('Principal ID of the managed identity to grant Cognitive Services OpenAI User role')
param managedIdentityPrincipalId string

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    customSubDomainName: name
    disableLocalAuth: disableLocalAuth
    publicNetworkAccess: 'Enabled'
  }
}

// GPT-4.1-mini — primary chat model (replaces retiring gpt-4o-mini)
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-41-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 8
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4.1-mini'
      version: '2025-04-14'
    }
  }
}

// text-embedding-3-small — cheaper and better than ada-002
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'text-embedding-3-small'
  sku: {
    name: 'Standard'
    capacity: 8
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
  }
  dependsOn: [chatDeployment]
}

// gpt-image-1-mini — image generation for scenes/portraits
resource imageDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-image-1-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-image-1-mini'
      version: '2025-10-06'
    }
  }
  dependsOn: [embeddingDeployment]
}

// Phi-4-mini — cheap reasoning for rules lookups and simple decisions
resource phiDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'Phi-4-mini-instruct'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'Microsoft'
      name: 'Phi-4-mini-instruct'
    }
  }
  dependsOn: [imageDeployment]
}

// Llama-4-Scout — open-weight storytelling for lore generation
resource llamaDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'Llama-4-Scout-17B-16E-Instruct'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'Meta'
      name: 'Llama-4-Scout-17B-16E-Instruct'
    }
  }
  dependsOn: [phiDeployment]
}

// Cognitive Services OpenAI User role for the managed identity
resource openAiUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundry.id, managedIdentityPrincipalId, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  scope: foundry
  properties: {
    // Cognitive Services OpenAI User
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('The endpoint URL for the AI Foundry resource')
output endpoint string = foundry.properties.endpoint

@description('The resource name')
output name string = foundry.name

@description('The resource ID')
output id string = foundry.id

@description('Primary API key (for local dev only)')
output apiKey string = foundry.listKeys().key1
```

- [ ] **Step 2: Validate Bicep syntax**

Run: `az bicep build --file infra/modules/ai-foundry.bicep`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add infra/modules/ai-foundry.bicep
git commit -m "infra: add Azure AI Foundry Bicep module with 5 model deployments"
```

---

### Task 2: Wire Foundry Module into main.bicep

**Files:**
- Modify: `infra/main.bicep`

- [ ] **Step 1: Remove old Azure OpenAI parameters and add Foundry module**

Replace the old `azureOpenAi*` parameters (lines 15-29) with a simpler set, and add the Foundry module call after the role-assignments module (line 160).

Remove these parameters:
- `azureOpenAiApiKey`
- `azureOpenAiEndpoint`
- `azureOpenAiChatDeployment`
- `azureOpenAiEmbeddingDeployment`
- `azureOpenAiDalleDeployment`

Add the Foundry module:
```bicep
// Create Azure AI Foundry resource with model deployments
module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'ai-foundry'
  scope: rg
  params: {
    name: '${environmentName}-ai-${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
  }
}
```

Add outputs:
```bicep
output AZURE_OPENAI_ENDPOINT string = aiFoundry.outputs.endpoint
output AZURE_AI_FOUNDRY_NAME string = aiFoundry.outputs.name
```

- [ ] **Step 2: Validate full Bicep template**

Run: `az bicep build --file infra/main.bicep`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add infra/main.bicep
git commit -m "infra: wire AI Foundry module into main deployment"
```

---

### Task 3: Update Dev Parameters and azure.yaml

**Files:**
- Modify: `infra/parameters/dev.bicepparam`
- Modify: `azure.yaml`

- [ ] **Step 1: Update dev parameters** — add uksouth location (already set), no OpenAI params needed since Foundry is self-contained

- [ ] **Step 2: Update azure.yaml postprovision hook** — remove references to manually setting OpenAI endpoint/key since Foundry provisions them automatically

- [ ] **Step 3: Commit**

```bash
git add infra/parameters/dev.bicepparam azure.yaml
git commit -m "infra: update dev params and azd hooks for Foundry"
```

---

### Task 4: Update Backend Config for New Model Names

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/azure_openai_client.py`

- [ ] **Step 1: Update config.py defaults**

Change `azure_openai_chat_deployment` default to `'gpt-41-mini'` (deployment name).
Change `azure_openai_mini_deployment` to `'Phi-4-mini-instruct'`.
Change `azure_openai_embedding_deployment` default to `'text-embedding-3-small'`.
Keep `azure_openai_dalle_deployment` as `'gpt-image-1-mini'`.

- [ ] **Step 2: Run backend tests**

Run: `cd /Users/chris.lloyd-jones/git/str-agentic-adventures && uv run pytest backend/tests/ -v --timeout=30 -x`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py
git commit -m "feat: update model deployment defaults for AI Foundry"
```

---

### Task 5: Initialize azd and Deploy

**Files:**
- No file changes — CLI operations

- [ ] **Step 1: Initialize azd environment**

```bash
cd /Users/chris.lloyd-jones/git/str-agentic-adventures
azd env new dev
azd env set AZURE_LOCATION uksouth
```

- [ ] **Step 2: Provision infrastructure**

```bash
azd provision --environment dev
```

This creates the resource group, all modules including AI Foundry with model deployments.

- [ ] **Step 3: If azd provision fails, fall back to direct Bicep deployment**

```bash
az deployment sub create \
  --location uksouth \
  --template-file infra/main.bicep \
  --parameters environmentName=dev location=uksouth resourceGroupName=str-dev-rg
```

- [ ] **Step 4: Deploy backend and frontend**

```bash
azd deploy --environment dev
```

Or if azd doesn't work, deploy manually:
1. Build and push Docker image to ACR
2. Deploy Container App
3. Build and deploy frontend to Static Web App

- [ ] **Step 5: Verify deployment**

```bash
# Get the backend URL from outputs
BACKEND_URL=$(azd env get-values | grep BACKEND | cut -d= -f2)
curl $BACKEND_URL/health
curl $BACKEND_URL/health/dependencies
```

---

### Task 6: End-to-End Testing with Playwright / Claude in Chrome

- [ ] **Step 1: Run Playwright E2E tests against deployed environment**

```bash
cd frontend && VITE_API_URL=$BACKEND_URL bun run test:e2e
```

- [ ] **Step 2: Manual browser testing with Claude in Chrome**

Test the full user flow:
1. Load the frontend URL
2. Create a campaign
3. Create a character
4. Send player input and verify AI responses
5. Test image generation
6. Check health/dependencies endpoint shows all services healthy

- [ ] **Step 3: Fix any issues found, redeploy, retest**

Use `/loop` to continuously test until everything passes.

---

### Task 7: Track Everything in GitHub Issues

- [ ] **Step 1: Create tracking issue for this deployment**

```bash
gh issue create --title "infra: deploy dev environment with Azure AI Foundry" \
  --label "infra" \
  --body "Deploy fresh dev environment with AI Foundry resource and 5 model deployments..."
```

- [ ] **Step 2: Update issues as work progresses**

Close issues and reference commits as each task completes.

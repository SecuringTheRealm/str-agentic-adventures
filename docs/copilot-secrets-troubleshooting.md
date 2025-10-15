# GitHub Copilot Agent Secret Configuration Troubleshooting

## Overview

This guide helps troubleshoot issues with Azure OpenAI secrets not being available to the GitHub Copilot coding agent.

## Problem: AZURE_OPENAI_API_KEY Not Available

### Symptoms

When running `scripts/test-azure-secrets.sh`, you see:

```
❌ AZURE_OPENAI_API_KEY is NOT set (required)
```

Even though other Azure secrets are available, and `COPILOT_AGENT_INJECTED_SECRET_NAMES` shows `AZURE_OPENAI_API_KEY`.

### Root Cause

The secret is configured as a **Copilot-specific secret** instead of a **regular repository secret**. GitHub Copilot handles these types of secrets differently:

- **Copilot-specific secrets**: Marked as "injected" but not accessible via `${{ secrets.* }}` in workflows
- **Regular repository secrets**: Accessible in workflows via `${{ secrets.* }}` and can be propagated to the Copilot agent environment

### Solution

Configure `AZURE_OPENAI_API_KEY` as a **regular repository secret**:

1. **Navigate to repository settings**:
   - Go to your repository on GitHub
   - Click **Settings** > **Secrets and variables** > **Actions**

2. **Check secret location**:
   - Look under **Repository secrets** (not Copilot secrets)
   - If `AZURE_OPENAI_API_KEY` is listed under a different section, delete it and recreate

3. **Add as repository secret**:
   - Click **New repository secret**
   - Name: `AZURE_OPENAI_API_KEY`
   - Value: Your Azure AI Foundry API key
   - Click **Add secret**

4. **Verify configuration**:
   - The `.github/workflows/copilot-setup-steps.yml` workflow will automatically propagate this secret to the Copilot agent environment
   - Run `scripts/test-azure-secrets.sh` in a new Copilot session to verify

## Required Secrets Configuration

### Minimal Configuration (Required)

These three secrets are **required** for basic functionality:

| Secret Name | Description | Where to Find |
|-------------|-------------|---------------|
| `AZURE_OPENAI_API_KEY` | Azure AI Foundry API key | [Azure AI Foundry](https://ai.azure.com) > Project Settings > Keys & Endpoint |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | [Azure AI Foundry](https://ai.azure.com) > Project Settings > Keys & Endpoint |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Chat model deployment name | [Azure AI Foundry](https://ai.azure.com) > Project > Deployments (e.g., `gpt-4o-mini`) |

### Optional Configuration

These secrets enable additional features:

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `AZURE_CLIENT_ID` | Service principal client ID | Azure resource deployment |
| `AZURE_OPENAI_API_VERSION` | API version override | Specific API version requirements |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model name | Document embeddings |
| `AZURE_OPENAI_DALLE_DEPLOYMENT` | DALL-E model name | Image generation |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | Azure resource deployment |
| `AZURE_TENANT_ID` | Azure tenant ID | Azure resource deployment |

## Secret Propagation Workflow

The `.github/workflows/copilot-setup-steps.yml` workflow automatically:

1. Reads secrets from `${{ secrets.* }}` context
2. Writes configured secrets to `$GITHUB_ENV`
3. Makes them available as environment variables to the Copilot agent
4. Reports configuration status in workflow summary

## Verification

### Test Secret Availability

Run the test script in your Copilot agent session:

```bash
bash scripts/test-azure-secrets.sh
```

Expected output for successful configuration:

```
🔍 Testing Azure OpenAI Secret Propagation...

Testing Required Azure Secrets:
================================

✅ AZURE_OPENAI_API_KEY is set
✅ AZURE_OPENAI_ENDPOINT is set
✅ AZURE_OPENAI_CHAT_DEPLOYMENT is set

Testing Optional Azure Secrets:
================================

...

Summary:
========

Required secrets: 3/3 configured
Optional secrets: X/6 configured

✅ Test PASSED: All required secrets are configured
```

### Check Workflow Summary

After the copilot-setup-steps workflow runs:

1. Go to your repository's **Actions** tab
2. Find the most recent **Copilot Setup Steps** workflow run
3. Check the **Summary** section for secret propagation status

It should show:

```
## Azure Secret Propagation Status

The following Azure secrets will be available to the Copilot coding agent:

✅ AZURE_OPENAI_API_KEY
✅ AZURE_OPENAI_ENDPOINT
✅ AZURE_OPENAI_CHAT_DEPLOYMENT
...
```

## Common Issues

### Issue: Secret marked as "injected" but not accessible

**Symptom**: `COPILOT_AGENT_INJECTED_SECRET_NAMES` shows the secret name, but the value isn't available

**Cause**: Secret is configured as Copilot-specific secret

**Fix**: Reconfigure as regular repository secret (see Solution section above)

### Issue: Secret value is empty in workflow

**Symptom**: Workflow shows `❌ AZURE_OPENAI_API_KEY (not configured)` in summary

**Cause**: Secret not configured or configured with wrong name

**Fix**: 
- Check secret name matches exactly (case-sensitive)
- Verify secret has a value (not empty)
- Ensure secret is in **Repository secrets** section

### Issue: All tests pass but backend still fails

**Symptom**: Test script passes but backend cannot authenticate

**Cause**: Backend is not reading environment variables correctly

**Fix**:
- Check backend logs for authentication errors
- Verify `backend/app/config.py` reads from environment variables
- Ensure backend server was restarted after environment changes

## Security Considerations

### Secret Masking

All secrets are automatically masked in GitHub Actions logs. You'll see `***` instead of actual values.

### Secret Storage

- Secrets are stored encrypted in GitHub
- Only available during workflow execution
- Not accessible in pull requests from forks

### Best Practices

- **Never commit secrets** to source code
- **Rotate secrets** regularly
- **Use minimal permissions** for service principals
- **Monitor secret usage** in Azure portal

## Additional Resources

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Repository Deployment Guide](./deployment.md)

## Getting Help

If you continue experiencing issues:

1. **Check workflow logs** for detailed error messages
2. **Verify Azure credentials** work outside of GitHub Actions
3. **Open an issue** with:
   - Output from `scripts/test-azure-secrets.sh`
   - Workflow run URL
   - Steps already attempted

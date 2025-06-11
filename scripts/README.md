# Scripts

This directory contains utility scripts for the Agentic Adventures project.

## Available Scripts

### validate_azure_openai.py

Validation script for Azure OpenAI integration setup as specified in ADR 0005.

**Usage:**
```bash
cd backend
python ../scripts/validate_azure_openai.py
```

**What it validates:**
- Environment variable configuration
- Required Python dependencies
- Azure OpenAI service connectivity
- Model deployment accessibility

**Prerequisites:**
- Python dependencies installed (`pip install -r requirements.txt`)
- Environment variables configured (copy `.env.example` to `.env` and configure)
- Azure OpenAI service provisioned and accessible

This script is referenced in the Azure OpenAI integration GitHub issue template and should be used to validate setup completion.
# str-agentic-adventures
 > AI-powered web app for tabletop RPGs that replaces the human Dungeon Master while maintaining creativity, flexibility, and immersion.

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/SecuringTheRealm/str-agentic-adventures/ci.yml?branch=main&label=CI)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/SecuringTheRealm/str-agentic-adventures/deploy-production.yml?branch=main&label=Production%20Deployment)
![GitHub issues](https://img.shields.io/github/issues/SecuringTheRealm/str-agentic-adventures)
![GitHub](https://img.shields.io/github/license/SecuringTheRealm/str-agentic-adventures)
![GitHub Repo stars](https://img.shields.io/github/stars/SecuringTheRealm/str-agentic-adventures?style=social)
[![Azure](https://custom-icon-badges.demolab.com/badge/Microsoft%20Azure-0089D6?logo=msazure&logoColor=white)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/?WT.mc_id=AI-MVP-5004204)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff)](#)

## Overview

Secure the Realm democratizes access to high-quality tabletop roleplaying experiences. The platform removes the need for a human Dungeon Master while preserving the creativity, flexibility, and immersion of traditional games. Anyone can instantly jump into an adventure tailored to their preferences and available time. Specialized AI agents work together to deliver a seamless and visually rich experience that adapts to player choices.



## Background and Problem Statement

Tabletop roleplaying games (TTRPGs) like Dungeons & Dragons have been a popular form of collaborative storytelling and gaming for decades. However, traditional TTRPGs require a Dungeon Master to orchestrate the game, create narratives, manage rules, and control non-player characters. This creates a significant barrier to entry for new players and those who cannot find a consistent group to play with. Additionally, the complex rules system can be intimidating for beginners and time-consuming even for experienced players.

Many potential players face significant barriers to enjoying tabletop roleplaying games: - Difficulty finding a skilled and available Dungeon Master - Challenges coordinating schedules among multiple players - Steep learning curve for game rules and mechanics - Limited access to visual aids and battle maps - Inconsistent gameplay experiences depending on the Dungeon Master's style and preparation - Inability to play spontaneously or on-demand - Lack of persistence in character development and campaign progression when groups disband

These barriers prevent many interested players from experiencing the rich storytelling and immersive gameplay that TTRPGs can offer, resulting in a significant unmet demand in the market.

## Architecture & Technical Stack

The Secure the Realm platform leverages:
- **Frontend**: TypeScript & React for a responsive user interface
- **Backend**: Python with Microsoft Semantic Kernel framework
- **AI Integration**: Azure OpenAI LLMs via Semantic Kernel plugins
- **Game Rules**: D&D 5e OGL SRD ruleset implementation ([reference docs](docs/reference/srd-5.2.1.md))
- **Real-time Features**: Immediate response to player actions
- **Data Management**: Structured storage for game elements and character data

### Multi-Agent System

Our architecture employs six specialized AI agents working in concert:

1. **Dungeon Master Agent**: Orchestrates gameplay and coordinates other agents
2. **Narrator Agent**: Manages campaign narratives and skill checks
3. **Scribe Agent**: Handles character sheets and game data
4. **Combat MC Agent**: Runs balanced combat encounters
5. **Combat Cartographer Agent**: Generates tactical battle maps
6. **Artist Agent**: Creates visual elements and character portraits

The system supports:
- Virtual dice rolling (d4-d100) with manual override
- Complete character management including leveling and feats
- Turn-based combat with initiative tracking
- Rich visual aids and battle maps
- Persistent campaign and character progression

## Deployment to Azure

This project supports both automated deployment through GitHub Actions and manual deployment using the Azure Developer CLI (azd).

### Quick Start - Manual Deployment

**Prerequisites**: Ensure you have an Azure AI Foundry project with deployed OpenAI models (see [local setup](#azure-ai-foundry-setup) for details).

1. Install [azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?WT.mc_id=AI-MVP-5004204).
2. Sign in to your Azure account:
   ```bash
   azd auth login
   ```
3. Set up your environment with your Azure AI Foundry credentials:
   ```bash
   azd env new <environment-name>
   azd env set AZURE_OPENAI_ENDPOINT <your-ai-foundry-endpoint>
   azd env set AZURE_OPENAI_API_KEY <your-ai-foundry-api-key>
   ```
4. Deploy all infrastructure and application code:
   ```bash
   azd up
   ```
   The command creates or updates Azure resources and then builds and deploys the app.

### GitHub Actions Deployment

The repository includes automated deployment workflows:

- **Production Deployment**: Automatically deploys to production when pushing to `main` branch (requires Azure secrets)
- **PR Environments**: Creates temporary environments for each pull request targeting `main` branch for testing
- **Environment Cleanup**: Automatically removes PR environments when pull requests are closed/merged

For setup instructions, see [Deployment Guide](docs/deployment.md).

### Required Azure Services

- **Azure AI Foundry project** with deployed OpenAI models (GPT-4o-mini, text-embedding-ada-002, DALL-E 3)
- **Azure Container Apps** for backend hosting
- **Azure Static Web Apps** for frontend hosting
- **Azure Storage Account** for file and image storage

> **Note**: Azure AI Foundry provides the unified platform for accessing Azure OpenAI models. Create your project at [ai.azure.com](https://ai.azure.com) to get started.

## Running the Application Locally

### Prerequisites

1. **Python 3.11 or higher** for the backend
2. **Node.js 18 or higher** for the frontend
3. **Azure AI Foundry access** for OpenAI models (see setup below)

### Azure AI Foundry Setup

To run the application locally, you need access to Azure OpenAI models through Azure AI Foundry:

1. **Create an Azure AI Foundry project**:
   - Go to [Azure AI Foundry](https://ai.azure.com)
   - Sign in with your Azure account
   - Create a new project or use an existing one

2. **Deploy required models**:
   - Navigate to **Deployments** in your Azure AI Foundry project
   - Deploy the following models:
     - **GPT-4o-mini** (for chat completion)
     - **text-embedding-ada-002** (for embeddings)
     - **DALL-E 3** (for image generation, optional)

3. **Get your endpoints and keys**:
   - In Azure AI Foundry, go to **Project settings**
   - Note your **Endpoint URL** (e.g., `https://your-project.openai.azure.com/`)
   - Go to **Keys and Endpoint** to get your **API key**

### Environment Configuration

1. **Backend setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env file with your Azure AI Foundry credentials:
   # AZURE_OPENAI_ENDPOINT=https://your-project.openai.azure.com/
   # AZURE_OPENAI_API_KEY=your-api-key-here
   # AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
   # AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   ```

2. **Install dependencies and start services**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   ./start.sh

   # Frontend (in a new terminal)
   cd frontend
   npm install
   npm start
   ```

The frontend will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8000`.

## Running Tests

Execute the backend test suite with `pytest`:

```bash
cd backend
python -m pytest tests/ -v
```

## Development Workflow

### 🔄 OpenAPI Client Synchronization

The frontend uses a generated TypeScript client from the backend's OpenAPI schema. **When backend API changes, developers must regenerate the frontend client.**

#### When to Regenerate

Regenerate the client after:
- ✅ Adding new API endpoints
- ✅ Modifying endpoint parameters or responses
- ✅ Changing data models or types
- ✅ Pulling backend changes from other developers

#### How to Regenerate

```bash
# 1. Start backend server
cd backend && python -m app.main

# 2. Regenerate frontend client  
cd frontend && npm run generate:api

# 3. Verify the update
npm run build && npm test
```

#### Automated Validation

Validate the entire workflow:
```bash
./scripts/validate-openapi-client.sh
```

See [docs/OPENAPI_CLIENT.md](docs/OPENAPI_CLIENT.md) for detailed documentation.

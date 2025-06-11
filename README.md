# str-agentic-adventures
 > AI-powered web app for tabletop RPGs that replaces the human Dungeon Master while maintaining creativity, flexibility, and immersion.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/SecuringTheRealm/str-agentic-adventures/CI)
![GitHub issues](https://img.shields.io/github/issues/SecuringTheRealm/str-agentic-adventures)
![GitHub](https://img.shields.io/github/license/SecuringTheRealm/str-agentic-adventures)
![GitHub Repo stars](https://img.shields.io/github/stars/SecuringTheRealm/str-agentic-adventures?style=social)
[![Azure](https://img.shields.io/badge/--3178C6?logo=microsoftazure&logoColor=ffffff)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/?WT.mc_id=AI-MVP-5004204)
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
- **Game Rules**: D&D 5e OGL SRD ruleset implementation
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

This project uses the **Azure Developer CLI (azd)** for provisioning cloud resources.

1. Install [azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?WT.mc_id=AI-MVP-5004204).
2. Sign in to your Azure account:
   ```bash
   azd auth login
   ```
3. Deploy all infrastructure and application code:
   ```bash
   azd up
   ```
   The command creates or updates Azure resources and then builds and deploys the app.

## Running the Application Locally

Start the backend and frontend separately:

```bash
# Backend
cd backend
./start.sh

# Frontend
cd ../frontend
npm install
npm start
```
The frontend is served at `http://localhost:3000` and expects the backend on `http://localhost:8000`.

## Running Tests

Execute the backend test suite with `pytest`:

```bash
cd backend
python -m pytest tests/ -v
```

# AI Dungeon Master - Product Requirements Document

## Background and Problem Statement

Tabletop roleplaying games (TTRPGs) like Dungeons & Dragons have been a popular form of collaborative storytelling and gaming for decades. However, traditional TTRPGs require a Dungeon Master to orchestrate the game, create narratives, manage rules, and control non-player characters. This creates a significant barrier to entry for new players and those who cannot find a consistent group to play with. Additionally, the complex rules system can be intimidating for beginners and time-consuming even for experienced players.

Many potential players face significant barriers to enjoying tabletop roleplaying games:
- Difficulty finding a skilled and available Dungeon Master
- Challenges coordinating schedules among multiple players
- Steep learning curve for game rules and mechanics
- Limited access to visual aids and battle maps
- Inconsistent gameplay experiences depending on the Dungeon Master's style and preparation
- Inability to play spontaneously or on-demand
- Lack of persistence in character development and campaign progression when groups disband

These barriers prevent many interested players from experiencing the rich storytelling and immersive gameplay that TTRPGs can offer, resulting in a significant unmet demand in the market.

## Product Vision Statement

Secure the Realm will democratize access to high-quality tabletop roleplaying experiences by providing an AI-powered platform that eliminates the need for a human Dungeon Master while preserving the creativity, flexibility, and immersion of traditional TTRPGs. Our vision is to create a system where anyone, anywhere can instantly jump into a personalized adventure tailored to their preferences, play style, and available time. Through specialized AI agents working in concert, we will deliver a seamless, engaging, and visually rich gaming experience that adapts to player choices and creates memorable stories worth sharing.

## Architecture

The Secure the Realm platform is built on the Python Microsoft Semantic Kernel framework, Typescript frontend. Semantic Kernel provides a multi-agent architecture, where each agent serves a specialized role in the tabletop RPG experience. Semantic Kernel will interface with Azure OpenAI LLMs using Python to enable the use of "plugins". This allows the LLMs to perform takes like storing and retrieving data. The Kernel enables the selection of the correct AI agent, function and plugin for the task at hand, rather than relying on a strict workflow.

## Agent Definitions

1. **Dungeon Master Agent (Orchestrator Agent)**
   - Primary user-facing agent that coordinates all other agents
   - Manages player interactions and conversation flow
   - Routes appropriate tasks to specialized agents
   - Maintains cohesion across the gameplay experience
   - Ensures continuity of game rules and narrative

2. **Narrator Agent**
   - Manages campaign narrative and storylines
   - Determines whether a skill check is required
   - Handles skill checks, and outcomes
   - Maintains campaign facts and story elements
   - Generates descriptions of environments, NPCs, and situations
   - Interprets player actions within the game world context
   - Stores key narrative data in structured format for recall

3. **Scribe Agent**
   - Manages character sheets and player data
   - Tracks inventory, equipment, and loot
   - Handles NPC data and attributes
   - Monitors spell slots, abilities, and resources
   - Manages character progression including level-ups, experience tracking, and ability score improvements
   - Enforces D&D 5e progression rules and validates character advancement
   - Maintains structured data records for lookup and recall excluding campaign data managed by Narrator

4. **Combat MC Agent**
   - Creates balanced encounter scenarios based on narrative context from Dungeon Master
   - Manages enemy tactics and behaviors
   - Track initiative order and combat state
   - Integrates with Combat Cartographer to ensure effective encounter details related to the battle map
   - Integrates with Narrator for narrative around combat outcomes

5. **Combat Cartographer Agent**
   - Generates tactical battle maps based on narrative context from Narrator

6. **Artist Agent**
   - Generates visual imagery based on narrative moments
   - Creates character portraits and NPC visualizations
   - Illustrates environments and locations
   - Produces visual aids for important items, maps, and scenes
   - Enhances immersion through visual storytelling

## Communication Flow

While the Dungeon Master serves as the orchestrator, agents can communicate directly with each other when appropriate:
- Agents share context and request information from each other as needed
- The Dungeon Master synthesizes responses from multiple agents into coherent player-facing output
- Each agent maintains its specialized knowledge domain while contributing to the whole experience
- Agent communication shall be determined by the Kernel on Microsoft Semantic Kernel

## Technical Requirements

### Core System

- **Framework**: Typescript frontend with Python backend leveraging Semantic Kernel Agents
 - **API Integration**: Microsoft Semantic Kernel for agentic implementation. Whilst the LLMs will be powered by Azure OpenAI endpoints, the Semantic Kernel framework provides a layer of abstraction
- **State Management**: Robust state tracking for game progression
- **Data Storage**: Structured data format for game elements, character sheets, and campaign information
- **Real-time Updates**: Immediate response to player actions

### Game Engine

- **Rules Implementation**: D&D 5e OGL SRD ruleset
- **Dice Rolling System**: Virtual dice implementation supporting all standard RPG dice (d4, d6, d8, d10, d12, d20, d100) and the ability of the user to bring their own dice by telling the DM what their roll or total score was
- **Character Management**: Character creation, leveling, and stat tracking in line with standard character sheets for 5th edition e.g. feats
- **Character Progression**: Experience-based leveling system with automatic proficiency bonus scaling, ability score improvements at appropriate levels (4, 8, 12, 16, 19), and hit point calculation using class-specific hit dice
- **Combat System**: Turn-based combat with initiative tracking and number of actions
- **Spell System**: Implementation of 5e spell mechanics and spell slots

### User Interface

- **Chat Interface**: Primary interaction through natural language conversation
- **Character Sheet Display**: Visual representation of character data available within the app
- **Map Visualization**: Display battle maps and illustrations separate to the chat interface the player is interacting with
- **Image Gallery**: Storage for generated artistic imagery and battle maps separate to the chat interface by the application (not the AI) saving that image and updating the image URL
- **Dice Roll Visibility**: Numeric feedback for dice outcomes where the game has rolled on behalf of the player, at the request of the player
- **Session History**: Summary record of game events and conversations


## Workflows

### Campaign Creation Workflow

1. Player describes desired campaign setting, tone, style and any homebrew rules
2. Dungeon Master coordinates with Narrator to establish world and setting
3. Artist generates world concept imagery which is then saved by the application, and then the image URL is updated in the 'art' window of the webapp
4. Dungeon Master guides players through character creation process
5. Scribe creates and populates templates for character creation based upon player instruction

### Gameplay Loop

1. Player inputs action or statement
2. Dungeon Master interprets and routes to appropriate agent(s)
3. Agent(s) process request and generate responses
4. Narrator updates narrative state as needed
5. Scribe updates character/world data as needed
6. Combat MC creates combat scenarios when triggered and when applicable only
7. Artist generates imagery for significant moments
8. Dungeon Master synthesizes responses and presents to player

### Combat Workflow

1. Combat MC establishes combat environment and participants
2. Scribe provides character and NPC statistics
3. Narrator provides narrative context
4. Combat Cartographer generates tactical map, and then the image URL is updated in the 'map' window of the webapp
5. Artist visualizes the battle scene
6. Combat rounds proceed through initiative order
7. Playertakes their actions and makes their decisions
8. Dungeon Master narrates combat outcomes and effects
9. Continue between Player and Combat MC working through each player and NPC's turns until the combat ends

## User Stories

### Player Stories

1. As a player, I want to create a D&D 5e character with standard race, class, and background options, so that I can start playing with a character I feel connected to.
2. As a player, I want to interact with a responsive AI Dungeon Master through natural language, so that I can focus on roleplaying instead of game mechanics.
3. As a player, I want to roll dice and perform skill checks for my character's actions, so that I can experience the excitement and unpredictability of tabletop gaming.
4. As a player, I want to engage in tactical combat with visual battle maps, so that I can make strategic decisions during encounters.
5. As a player, I want to see visual representations of important scenes and characters, so that I can better immerse myself in the game world.
6. As a player, I want to track my character's inventory, spells, and abilities, so that I can manage my resources effectively during gameplay.
7. As a player, I want to experience a coherent and dynamic campaign narrative, so that my actions feel meaningful within the story.
8. As a player, I want to have my character's backstory integrated into the ongoing campaign, so that my character feels like a natural part of the world.
9. As a player, I want to gain experience points and level up my character, so that I can see meaningful progression and unlock new abilities over time.
10. As a player, I want to make ability score improvements when my character reaches appropriate levels, so that I can customize my character's development according to my playstyle.
11. As a player, I want to save and resume gameplay sessions, so that I can enjoy the campaign over multiple playing sessions without losing progress.

### Dungeon Master (AI) Stories

1. As a Dungeon Master (AI), I want to coordinate all aspects of the game world seamlessly, so that players experience a cohesive gameplay environment.
2. As a Dungeon Master (AI), I want to generate balanced encounters appropriate to party level and composition, so that combat remains challenging but fair.
3. As a Dungeon Master (AI), I want to maintain consistent NPCs with distinct personalities, so that the game world feels authentic and inhabited by believable characters.
4. As a Dungeon Master (AI), I want to create compelling narrative arcs responsive to player choices, so that players feel their decisions have meaningful impact on the story.
5. As a Dungeon Master (AI), I want to provide rule clarifications and adjudicate player actions, so that gameplay remains smooth and accessible.
6. As a Dungeon Master (AI), I want to generate evocative descriptions of environments and situations, so that players can visualize and immerse themselves in the world.
7. As a Dungeon Master (AI), I want to track multiple threads of story and character development, so that the campaign maintains continuity and depth.
8. As a Dungeon Master (AI), I want to manage character progression and enforce D&D 5e advancement rules, so that character development remains balanced and true to the game system.
9. As a Dungeon Master (AI), I want to create a sense of immersion and agency for players, so that they feel emotionally invested in the game experience.

## Implementation Phases

### Phase 1: Core Agent Framework

- Implement the multi-agent architecture with Dungeon Master as orchestrator
- Develop basic prompt engineering for each specialized agent
- Create core data models for characters, campaigns, and game state
- Build the chat interface for player interaction

### Phase 2: Game Rules Implementation

- Integrate D&D 5e OGL SRD ruleset
- Implement dice rolling and skill check system
- Create character creation and management workflows
- Develop basic combat mechanics

### Phase 3: Enhanced Agent Intelligence

- Refine agent specializations with improved prompts
- Implement inter-agent communication protocols
- Enhance knowledge storage and retrieval for campaign data
- Develop narrative memory and consistency features

### Phase 4: Visual Elements

- Integrate Art Master agent for image generation
- Implement battle map creation system
- Add character portrait generation
- Create environment visualization capabilities

### Phase 5: Advanced Features

- Add campaign persistence and save/load functionality
- Implement multi-player support
- Create campaign sharing capabilities
- Develop custom content creation tools

## Open Game License Compliance

- All game mechanics will adhere to the OGL SRD for D&D 5e
- Proper attribution for OGL content will be maintained
- Non-OGL content will be clearly separated from OGL content
- Terms of use will include appropriate OGL notices

## Success Metrics

- Player engagement duration per session
- Campaign completion rates
- Character progression metrics ✅ **Implemented**: Experience tracking, level-ups, and ability score improvements
- Narrative coherence and continuity from player feedback
- Combat balance and tactical satisfaction from player feedback
- Image generation quality and relevance from player feedback
- User satisfaction with agent responses from player feedback
- System stability and response times based upon terminal data on execution as well as player feedback

## Conclusion

The AI Dungeon Master platform represents a next-generation roleplaying games, representing the convergence of Tabletop Roleplaying Games with their sister Computer Roleplaying Games, as well as a step change of depending upon procedural generation or the dungeon master role for creating unique experiences - Through leveraging specialized AI agents to create a rich, immersive experience while maintaining the core essence of D&D 5e gameplay. By distributing responsibilities across specialized agents while maintaining a cohesive player experience, the system aims to provide an accessible yet deep roleplaying experience for both new and experienced players.

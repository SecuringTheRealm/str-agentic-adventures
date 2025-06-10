# str-agentic-adventures
> AI-powered web app for tabletop RPGs that replaces the human Dungeon Master while maintaining creativity, flexibility, and immersion.

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/SecuringTheRealm/str-agentic-adventures/CI)
![GitHub issues](https://img.shields.io/github/issues/SecuringTheRealm/str-agentic-adventures)
![GitHub](https://img.shields.io/github/license/SecuringTheRealm/str-agentic-adventures)
![GitHub Repo stars](https://img.shields.io/github/stars/SecuringTheRealm/str-agentic-adventures?style=social)
[![Azure](https://img.shields.io/badge/--3178C6?logo=microsoftazure&logoColor=ffffff)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/?WT.mc_id=AI-MVP-5004204)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff)](#)

Secure the Realm will democratize access to high-quality tabletop roleplaying experiences by providing an AI-powered platform that eliminates the need for a human Dungeon Master while preserving the creativity, flexibility, and immersion of traditional TTRPGs. Our vision is to create a system where anyone, anywhere can instantly jump into a personalized adventure tailored to their preferences, play style, and available time. Through specialized AI agents working in concert, we will deliver a seamless, engaging, and visually rich gaming experience that adapts to player choices and creates memorable stories worth sharing.

## Background and Problem Statement

Tabletop roleplaying games (TTRPGs) like Dungeons & Dragons have been a popular form of collaborative storytelling and gaming for decades. However, traditional TTRPGs require a Dungeon Master to orchestrate the game, create narratives, manage rules, and control non-player characters. This creates a significant barrier to entry for new players and those who cannot find a consistent group to play with. Additionally, the complex rules system can be intimidating for beginners and time-consuming even for experienced players.

Many potential players face significant barriers to enjoying tabletop roleplaying games: - Difficulty finding a skilled and available Dungeon Master - Challenges coordinating schedules among multiple players - Steep learning curve for game rules and mechanics - Limited access to visual aids and battle maps - Inconsistent gameplay experiences depending on the Dungeon Master's style and preparation - Inability to play spontaneously or on-demand - Lack of persistence in character development and campaign progression when groups disband

These barriers prevent many interested players from experiencing the rich storytelling and immersive gameplay that TTRPGs can offer, resulting in a significant unmet demand in the market.

## Architecture
The Secure the Realm platform is built on the Python Microsoft Semantic Kernel framework, with a frontend in TypeScript. Semantic Kernel provides a multi-agent architecture, where each agent serves a specialized role in the tabletop RPG experience. Semantic Kernel will interface with Azure OpenAI LLMs using Python to enable the use of "plugins". This allows the LLMs to perform takes like storing and retrieving data. The Kernel enables the selection of the correct AI agent, function and plugin for the task at hand, rather than relying on a strict workflow.
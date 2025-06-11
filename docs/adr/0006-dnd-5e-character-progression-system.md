# D&D 5e Character Progression System Implementation

* Status: accepted
* Date: 2025-06-11

## Context and Problem Statement

The AI Dungeon Master platform requires a robust character progression system that allows players to advance their characters according to D&D 5e rules. Players need to gain experience points, level up, improve ability scores, and gain hit points in a way that maintains game balance and follows official D&D 5e SRD guidelines. Without proper progression mechanics, the platform would not provide the long-term engagement and character development that is fundamental to the D&D experience.

## Decision Drivers

* D&D 5e SRD compliance for all progression mechanics
* Automated validation to prevent rule violations and maintain game balance
* Experience-based leveling system that provides clear advancement goals
* Support for ability score improvements at appropriate levels
* Hit point calculation that accounts for class differences and Constitution modifiers
* Prevention of over-allocation of character improvements
* Integration with existing character management and agent architecture

## Considered Options

* Option 1: Experience-based leveling with full D&D 5e compliance
    * Implement exact D&D 5e experience thresholds and progression rules
    * Automatic proficiency bonus scaling and ability score improvement tracking
    * Class-specific hit dice and hit point calculations
    * Pros: True to D&D 5e experience, familiar to players, provides clear advancement goals
    * Cons: More complex implementation, requires careful validation logic

* Option 2: Milestone-based leveling system
    * Players advance based on story milestones rather than experience points
    * Simplified progression without XP tracking
    * Pros: Simpler implementation, narrative-focused advancement
    * Cons: Less player agency, doesn't match traditional D&D experience, harder to implement fairly in AI-driven content

* Option 3: Hybrid point-buy advancement system
    * Custom progression system using generic advancement points
    * Players allocate points to different character aspects
    * Pros: Flexible character customization, unique to the platform
    * Cons: Not D&D 5e compliant, confusing to D&D players, requires extensive balancing

## Decision Outcome

Chosen option: "Experience-based leveling with full D&D 5e compliance"

Justification:
* Maintains fidelity to D&D 5e rules that players expect and understand
* Provides clear, quantifiable advancement goals through experience points
* Integrates naturally with combat and quest reward systems
* Allows for proper implementation of all D&D 5e progression features including ability score improvements
* Enables proper game balance through tested D&D 5e mechanics

## Consequences

### Positive
* Players experience familiar and predictable character advancement
* Full compatibility with D&D 5e character builds and progression strategies
* Automated validation prevents common rule mistakes and maintains game balance
* Clear integration points for future features like feats and multiclassing
* Supports long-term campaign play with meaningful character development

### Negative
* More complex implementation requiring detailed knowledge of D&D 5e progression rules
* Requires comprehensive validation logic to prevent rule violations
* Experience point awards must be carefully balanced by AI systems
* Additional data tracking for ability score improvements and hit dice

### Risks and Mitigations
* Risk: Incorrect implementation of D&D 5e rules leading to unbalanced characters
  * Mitigation: Comprehensive testing against official D&D 5e progression tables and rules
* Risk: Experience point inflation or deflation affecting game balance
  * Mitigation: AI systems trained on appropriate D&D 5e encounter and quest reward guidelines
* Risk: Players finding ways to exploit progression system
  * Mitigation: Server-side validation of all character modifications and progression requests

## Implementation Details

### Core Components Added
* `RulesEnginePlugin` methods for progression calculations:
  * `calculate_level()` - XP to level conversion using official D&D 5e thresholds
  * `calculate_proficiency_bonus()` - Level-based proficiency bonus scaling
  * `check_asi_eligibility()` - Validates ability score improvement availability
  * `calculate_level_up_hp()` - Class-specific hit point calculation

### API Endpoints
* `POST /character/{id}/level-up` - Handles character level advancement
* `POST /character/{id}/award-experience` - Awards experience points with level-up checking
* `GET /character/{id}/progression-info` - Provides progression status and eligibility

### Data Model Enhancements
* `CharacterSheet.ability_score_improvements_used` - Tracks ASI usage
* `CharacterSheet.hit_dice` - Stores class-specific hit dice for HP calculations
* `LevelUpRequest/Response` models for structured level-up operations

## Links

* Related ADRs: [ADR-0001 Semantic Kernel Multi-Agent Framework](0001-semantic-kernel-multi-agent-framework.md)
* Related ADRs: [ADR-0002 Specialized Multi-Agent Architecture](0002-specialized-multi-agent-architecture.md)
* References: [D&D 5e SRD Character Advancement](https://dnd.wizards.com/resources/systems-reference-document)
* References: Product Requirements Document - Character progression metrics
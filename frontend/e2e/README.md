# E2E Tests for Securing the Realm - Agentic Adventures

This directory contains end-to-end (E2E) tests using Playwright to validate the key user flows and D&D 5e SRD compliance of the AI Dungeon Master application.

## Test Structure

### 1. Basic Application Flow (`basic-flow.spec.ts`)
- Validates application loading
- Checks initial UI state
- Basic smoke tests

### 2. Campaign Creation Flow (`campaign-creation.spec.ts`)
- Tests campaign creation interface
- Validates custom campaign creation
- Tests campaign template selection
- Ensures proper campaign configuration options

### 3. Character Creation Flow (`character-creation.spec.ts`)
- Tests D&D 5e character creation
- Validates character selection options
- Tests predefined character browsing
- Ensures proper character form validation

### 4. Game Session Flow (`game-session.spec.ts`)
- Tests complete game session startup
- Validates AI Dungeon Master interaction
- Tests dice rolling functionality
- Validates character sheet display
- Tests combat interface
- Tests save/load functionality

### 5. SRD Compliance Tests (`srd-compliance.spec.ts`)
- Validates D&D 5e System Reference Document compliance
- Tests race and class restrictions to SRD-approved options
- Validates ability score rules (3-20 range)
- Tests standard dice rolling (d4, d6, d8, d10, d12, d20, d100)
- Validates level progression and proficiency bonus rules
- Tests spell system for spellcasting classes

### 6. Complete User Journey (`user-journey.spec.ts`)
- Comprehensive end-to-end user flow test
- Manual testing simulation from user perspective
- Step-by-step journey documentation
- Accessibility and usability testing

## Key Game Flows Tested

Based on the Product Requirements Document and D&D 5e SRD, these tests cover:

### Primary User Stories
1. **Campaign Creation**: "Create a D&D 5e campaign with appropriate settings"
2. **Character Creation**: "Create a D&D 5e character with standard race, class, and background options"
3. **AI DM Interaction**: "Interact with a responsive AI Dungeon Master through natural language"
4. **Dice Rolling**: "Roll dice and perform skill checks for character actions"
5. **Combat System**: "Engage in tactical combat with visual battle maps"
6. **Character Progression**: "Gain experience points and level up character"

### D&D 5e SRD Compliance
- **Races**: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling
- **Classes**: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
- **Ability Scores**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma (3-20 range)
- **Standard Dice**: d4, d6, d8, d10, d12, d20, d100
- **Level 1 Starting Rules**: 0 XP, +2 proficiency bonus

## Running the Tests

### Prerequisites
1. Frontend application running on `http://127.0.0.1:5173`
2. Playwright browsers installed (`npx playwright install`)

### Commands
```bash
# Run all E2E tests
npm run test:e2e

# Run tests with UI mode for debugging
npm run test:e2e:ui

# Run tests in debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test campaign-creation.spec.ts

# Run tests with headed browser (visible)
npx playwright test --headed
```

### Test Configuration
Tests are configured in `playwright.config.ts` with:
- Base URL: `http://127.0.0.1:5173`
- Multiple browser testing (Chromium, Firefox, WebKit)
- Automatic dev server startup
- Screenshot capture on failure
- Trace collection for debugging

## Screenshots and Artifacts

Tests automatically capture screenshots at key points:
- `screenshots/journey/` - Complete user journey documentation
- `screenshots/` - Individual test screenshots
- Test artifacts stored in `test-results/` directory

## Test Philosophy

These tests are designed to:
1. **Simulate Real User Behavior**: Tests follow actual user workflows
2. **Validate D&D 5e Compliance**: Ensure adherence to official SRD rules
3. **Test Key Product Features**: Cover all major user stories from PRD
4. **Provide Documentation**: Screenshots serve as visual documentation
5. **Enable Regression Testing**: Catch breaks in core functionality

## Troubleshooting

### Common Issues
1. **Application not starting**: Ensure `npm run dev -- --host 127.0.0.1 --port 5173` is running
2. **Browser download fails**: Try `npx playwright install chromium` individually
3. **Tests timeout**: Increase timeout in playwright.config.ts
4. **Screenshots missing**: Check file permissions in screenshots directory

### Debugging Tips
1. Use `--headed` flag to see browser actions
2. Add `await page.pause()` to stop execution at specific points
3. Check `test-results/` for failure artifacts
4. Use `--debug` flag for step-by-step execution

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Include appropriate comments and console.log statements
3. Capture screenshots at key interaction points
4. Validate against D&D 5e SRD requirements
5. Test both success and failure scenarios
6. Ensure tests are deterministic and not flaky

## Related Documentation
- [Product Requirements Document](../../docs/prd/index.md)
- [D&D 5e SRD Reference](../../docs/reference/srd-5.2.1.md)
- [Application Architecture](../../README.md)

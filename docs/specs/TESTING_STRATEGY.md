# Testing Strategy Improvements

This document outlines the testing strategy improvements implemented for the Securing the Realm - Agentic Adventures project.

## Overview

The testing strategy has been enhanced with:
- Factory pattern for test data generation
- Parameterized tests for combat scenarios
- Async test support
- Split CI workflows for efficiency
- Performance monitoring with duration reporting

## Test Organization

### Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Fast unit tests (< 0.1s each)
- `@pytest.mark.integration`: Integration tests that may take longer
- `@pytest.mark.slow`: Performance tests and large-scale scenarios
- `@pytest.mark.asyncio`: Async tests (handled automatically)

### Running Tests by Category

```bash
# Run only fast unit tests
pytest -m "unit or not slow"

# Run only integration tests
pytest -m "integration"

# Run only slow tests
pytest -m "slow"

# Exclude slow tests (for CI fast feedback)
pytest -m "not slow"
```

## Factory Pattern

### Available Factories

Located in `backend/tests/factories.py`:

- `CharacterFactory`: Generic D&D character data
- `FighterCharacterFactory`: Fighter-specific character data
- `WizardCharacterFactory`: Wizard-specific character data
- `CampaignFactory`: Campaign creation data
- `CombatEncounterFactory`: Combat encounter scenarios
- `AttackActionFactory`: Basic attack actions
- `SpellAttackActionFactory`: Spell attack actions
- `SpellDamageActionFactory`: Area/save spell actions
- `SkillCheckActionFactory`: Skill check scenarios
- `SavingThrowActionFactory`: Saving throw scenarios

### Usage Examples

```python
def test_character_creation(self, fighter_character_factory):
    """Test using factory fixture."""
    character_data = fighter_character_factory()
    
    assert character_data["character_class"] == "fighter"
    assert character_data["armor_class"] >= 15

def test_custom_character():
    """Test with custom factory parameters."""
    character = FighterCharacterFactory(
        name="Custom Fighter",
        abilities__strength=18  # Override nested factory
    )
    
    assert character["name"] == "Custom Fighter"
    assert character["abilities"]["strength"] == 18
```

## Parameterized Tests

### Combat Action Testing

Instead of duplicate test methods for each combat scenario:

```python
# OLD APPROACH - Multiple similar test methods
def test_sword_attack(self):
    action_data = {"type": "attack", "weapon": "sword", ...}
    # test logic

def test_bow_attack(self):
    action_data = {"type": "attack", "weapon": "bow", ...}
    # same test logic

# NEW APPROACH - Parameterized test
@pytest.mark.parametrize("weapon,damage,expected_range", [
    ("sword", "1d8+3", (4, 11)),
    ("bow", "1d8+2", (3, 10)),
    ("greataxe", "1d12+4", (5, 16)),
])
def test_weapon_attacks(self, weapon, damage, expected_range):
    action_data = AttackActionFactory(weapon=weapon, damage=damage)
    # single test method handles all scenarios
```

### Skill Check Variations

```python
@pytest.mark.parametrize("skill,ability,proficient", [
    ("perception", 13, True),
    ("stealth", 14, False),
    ("investigation", 12, True),
])
def test_skill_checks(self, skill, ability, proficient):
    action_data = SkillCheckActionFactory(
        skill=skill,
        ability_score=ability,
        proficient=proficient
    )
    # Test different skill configurations
```

## Performance Monitoring

### Duration Reporting

Test durations are automatically reported with the 10 slowest tests:

```bash
# In pytest.ini
addopts = ["--durations=10"]
```

### Identifying Hotspots

Use `--durations=20` for more detailed reporting:

```bash
pytest --durations=20
```

### Performance Regression Tests

```python
@pytest.mark.slow
@pytest.mark.parametrize("encounter_size,max_time", [
    (1, 0.1),   # Single enemy should be fast
    (5, 0.5),   # Medium encounter
    (10, 1.0),  # Large encounter
])
def test_combat_performance(self, encounter_size, max_time):
    start_time = time.time()
    # ... combat processing ...
    duration = time.time() - start_time
    assert duration < max_time
```

## CI/CD Improvements

### Split Workflows

1. **Fast Unit Tests** (`unit-tests.yml`)
   - Runs on every PR and push
   - Tests marked as `unit` or not `slow`
   - Quick feedback for developers

2. **Integration Tests** (`integration-tests.yml`)
   - Runs on main branch pushes and nightly
   - Tests marked as `integration` or `slow`
   - Comprehensive backend validation

3. **E2E Tests** (`e2e-tests.yml`)
   - Runs on main branch changes and nightly
   - Playwright end-to-end tests
   - Full user journey validation

### Runner Efficiency

- Unit tests run on every change for fast feedback
- Expensive tests run nightly to save runner minutes
- Path-based filtering prevents unnecessary runs

## Frontend Testing

### Testing Library Improvements

Replaced `querySelector` with semantic Testing Library queries:

```javascript
// OLD - Tightly coupled to CSS
expect(document.querySelector('.typing-indicator')).toBeInTheDocument();

// NEW - Semantic and accessible
expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
```

### Benefits

- Tests remain stable when CSS changes
- Better accessibility testing
- Clearer test intent

## Migration Guide

### Converting Existing Tests

1. **Replace hardcoded data with factories:**
   ```python
   # Before
   character_data = {
       "name": "Test Fighter",
       "race": "human",
       "character_class": "fighter",
       "abilities": {"strength": 16, "dexterity": 14, ...}
   }
   
   # After
   character_data = FighterCharacterFactory()
   ```

2. **Parameterize similar test cases:**
   ```python
   # Before: Multiple test methods
   def test_fireball_damage(self): ...
   def test_lightning_bolt_damage(self): ...
   
   # After: One parameterized test
   @pytest.mark.parametrize("spell,damage_type", [
       ("fireball", "fire"),
       ("lightning_bolt", "lightning"),
   ])
   def test_spell_damage(self, spell, damage_type): ...
   ```

3. **Add appropriate markers:**
   ```python
   @pytest.mark.unit  # Fast tests
   @pytest.mark.integration  # Cross-component tests
   @pytest.mark.slow  # Performance/large-scale tests
   ```

## Best Practices

1. **Use factories for all test data** - Reduces duplication and improves maintainability
2. **Parameterize similar scenarios** - Single test method for multiple inputs
3. **Mark tests appropriately** - Enables selective test running
4. **Monitor test performance** - Keep unit tests fast, identify slow tests
5. **Use semantic queries** - Testing Library queries over CSS selectors
6. **Split CI appropriately** - Fast feedback vs comprehensive testing

## Tools Used

- **pytest**: Test framework with parametrization and markers
- **pytest-asyncio**: Async test support
- **pytest-factoryboy**: Factory pattern for test data
- **factory_boy**: Object factory library
- **Testing Library**: Semantic frontend testing queries
- **Playwright**: End-to-end testing framework

### Playwright MCP Helper Commands

Generate and refine E2E coverage faster by using the Codex Playwright MCP workflow described in the official guide: https://blog.gopenai.com/automating-e2e-chat-flow-testing-with-codex-playwright-mcp-1ce4020dcbca. The workflow provides three Claude code commands:

- `pw-explore-website` — map page structure, surface selectors, and collect candidate flows.
- `pw-generate-tests` — scaffold Playwright specs for the discovered journeys.
- `pw-manual-testing` — capture manual QA notes while stepping through the UI.

Adopt these commands whenever Playwright scenarios change to keep exploratory, generated, and manual testing aligned.

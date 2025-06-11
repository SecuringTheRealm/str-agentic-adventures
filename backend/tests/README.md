# Backend Test Suite

This directory contains comprehensive tests for the AI Dungeon Master backend application.

## Test Structure

### `test_models.py`
Comprehensive tests for all Pydantic models including:
- **Enum validation**: CharacterClass, Race, Ability, CombatState
- **Model creation and validation**: Abilities, HitPoints, Item, Spell, CharacterSheet
- **Request/Response models**: CreateCharacterRequest, PlayerInput, GameResponse, Campaign models
- **Validation error handling**: Testing required fields and data types
- **Default value verification**: Ensuring models have correct default values
- **UUID generation**: Testing auto-generated IDs

### `test_agents.py`
Tests for agent interface contracts and mocking:
- **Agent interface testing**: Verifying expected behavior of agent classes without dependencies
- **Mock agent functionality**: Testing agent interactions through mocking
- **Async operation support**: Testing asynchronous agent methods
- **Agent communication patterns**: Testing how agents would interact in the system

### `test_integration.py`
Integration tests for system components:
- **Model compatibility**: Testing that request/response models work together
- **Data validation flows**: End-to-end validation testing
- **Serialization/deserialization**: Testing model data conversion
- **System integration**: Testing component interactions without external dependencies

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run specific test categories:
```bash
# Models only
python -m pytest tests/test_models.py -v

# Agents only
python -m pytest tests/test_agents.py -v

# Integration only
python -m pytest tests/test_integration.py -v
```

### Run with coverage (if coverage.py is installed):
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## Test Configuration

Tests are configured via `pyproject.toml` with the following settings:
- Test discovery in `tests/` directory
- Verbose output by default
- Strict marker and config checking
- Custom test markers for categorization

## Test Philosophy

This test suite focuses on:

1. **Unit Testing**: Testing individual components in isolation
2. **Contract Testing**: Ensuring interfaces behave as expected
3. **Validation Testing**: Verifying data validation works correctly
4. **Integration Testing**: Testing component interactions
5. **Mocking External Dependencies**: Avoiding external API calls during testing

## Key Features Tested

- ✅ Pydantic model validation and serialization
- ✅ Enum value correctness
- ✅ Required field validation
- ✅ Default value assignment
- ✅ UUID generation for models
- ✅ Agent interface contracts
- ✅ Async operation support
- ✅ Request/response model compatibility
- ✅ Data type validation
- ✅ Error handling for invalid data

## Dependencies

The test suite uses:
- `pytest`: Test framework
- `pytest-asyncio`: Async test support (via anyio plugin)
- `unittest.mock`: Mocking external dependencies
- `pydantic`: Model validation testing
- Standard library modules for UUID, datetime testing

### `test_adr_compliance.py`
Comprehensive validation tests for ADR implementation compliance:
- **ADR Implementation Verification**: Testing that all architectural decisions are properly implemented
- **File Structure Validation**: Ensuring required components exist and contain expected implementations
- **Integration Validation**: Testing that components are properly integrated (agents with storage, etc.)
- **Compliance Scoring**: Automated verification of ADR compliance status

## Notes

- Tests are designed to run without external dependencies (Azure OpenAI, databases, etc.)
- Complex FastAPI integration tests were intentionally simplified to focus on testable components
- Agent tests use mocking to avoid Semantic Kernel dependency issues
- ADR compliance tests validate actual implementation exists and is integrated correctly
- All tests pass reliably and provide good coverage of the core functionality

## Test Results

Current test suite: **36+ tests covering core functionality plus ADR compliance validation** ✅

This provides comprehensive test coverage for the core backend functionality, architectural compliance, and maintains simplicity and reliability.
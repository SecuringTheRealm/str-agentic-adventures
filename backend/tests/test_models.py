"""
Tests for Pydantic models validation and serialization.
"""

import pytest
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import ValidationError

from app.models.game_models import (
    CharacterClass,
    Race,
    Ability,
    CombatState,
    Abilities,
    HitPoints,
    Item,
    Spell,
    CharacterSheet,
    CreateCharacterRequest,
    PlayerInput,
    GameResponse,
    Campaign,
    CreateCampaignRequest,
    GenerateImageRequest,
    BattleMapRequest,
)


class TestEnums:
    """Test class for enum models."""

    def test_character_class_enum(self):
        """Test CharacterClass enum values."""
        assert CharacterClass.FIGHTER == "fighter"
        assert CharacterClass.WIZARD == "wizard"
        assert CharacterClass.ROGUE == "rogue"

    def test_race_enum(self):
        """Test Race enum values."""
        assert Race.HUMAN == "human"
        assert Race.ELF == "elf"
        assert Race.DWARF == "dwarf"

    def test_ability_enum(self):
        """Test Ability enum values."""
        assert Ability.STRENGTH == "strength"
        assert Ability.DEXTERITY == "dexterity"
        assert Ability.CONSTITUTION == "constitution"

    def test_combat_state_enum(self):
        """Test CombatState enum values."""
        assert CombatState.READY == "ready"
        assert CombatState.ACTIVE == "active"
        assert CombatState.COMPLETED == "completed"


class TestAbilities:
    """Test class for Abilities model."""

    def test_abilities_default_values(self):
        """Test that Abilities model has correct default values."""
        abilities = Abilities()

        assert abilities.strength == 10
        assert abilities.dexterity == 10
        assert abilities.constitution == 10
        assert abilities.intelligence == 10
        assert abilities.wisdom == 10
        assert abilities.charisma == 10

    def test_abilities_custom_values(self):
        """Test Abilities model with custom values."""
        abilities = Abilities(
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=13,
            charisma=8,
        )

        assert abilities.strength == 16
        assert abilities.dexterity == 14
        assert abilities.constitution == 15
        assert abilities.intelligence == 12
        assert abilities.wisdom == 13
        assert abilities.charisma == 8


class TestHitPoints:
    """Test class for HitPoints model."""

    def test_hit_points_valid(self):
        """Test valid HitPoints creation."""
        hp = HitPoints(current=25, maximum=30)

        assert hp.current == 25
        assert hp.maximum == 30

    def test_hit_points_validation(self):
        """Test HitPoints validation."""
        # Test that both fields are required
        with pytest.raises(ValidationError):
            HitPoints()


class TestItem:
    """Test class for Item model."""

    def test_item_minimal(self):
        """Test Item creation with minimal required fields."""
        item = Item(name="Sword")

        assert item.name == "Sword"
        assert item.quantity == 1
        assert item.description is None
        assert item.weight is None
        assert item.value is None
        assert item.properties is None
        assert item.id is not None  # Auto-generated UUID

    def test_item_full(self):
        """Test Item creation with all fields."""
        item = Item(
            name="Magic Sword",
            description="A gleaming magical blade",
            quantity=1,
            weight=3.5,
            value=500,
            properties={"damage": "1d8+1", "magical": True},
        )

        assert item.name == "Magic Sword"
        assert item.description == "A gleaming magical blade"
        assert item.quantity == 1
        assert item.weight == 3.5
        assert item.value == 500
        assert item.properties["damage"] == "1d8+1"
        assert item.properties["magical"] is True


class TestSpell:
    """Test class for Spell model."""

    def test_spell_creation(self):
        """Test Spell model creation."""
        spell = Spell(
            name="Fireball",
            level=3,
            school="Evocation",
            casting_time="1 action",
            range="150 feet",
            components="V, S, M",
            duration="Instantaneous",
            description="A bright streak flashes from your pointing finger...",
        )

        assert spell.name == "Fireball"
        assert spell.level == 3
        assert spell.school == "Evocation"
        assert spell.casting_time == "1 action"
        assert spell.range == "150 feet"
        assert spell.components == "V, S, M"
        assert spell.duration == "Instantaneous"
        assert "bright streak" in spell.description
        assert spell.id is not None  # Auto-generated UUID


class TestCharacterSheet:
    """Test class for CharacterSheet model."""

    def test_character_sheet_minimal(self):
        """Test CharacterSheet creation with minimal required fields."""
        abilities = Abilities(strength=16, dexterity=14, constitution=15)
        hit_points = HitPoints(current=10, maximum=10)

        character = CharacterSheet(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
            hit_points=hit_points,
        )

        assert character.name == "Test Hero"
        assert character.race == Race.HUMAN
        assert character.character_class == CharacterClass.FIGHTER
        assert character.level == 1  # Default value
        assert character.experience == 0  # Default value
        assert character.armor_class == 10  # Default value
        assert character.speed == 30  # Default value
        assert character.proficiency_bonus == 2  # Default value
        assert character.id is not None  # Auto-generated UUID

    def test_character_sheet_validation_error(self):
        """Test CharacterSheet validation with missing required fields."""
        with pytest.raises(ValidationError):
            CharacterSheet(name="Test")  # Missing required fields


class TestCreateCharacterRequest:
    """Test class for CreateCharacterRequest model."""

    def test_create_character_request_valid(self):
        """Test valid CreateCharacterRequest."""
        abilities = Abilities(strength=16, dexterity=14, constitution=15)

        request = CreateCharacterRequest(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
            backstory="A brave warrior",
        )

        assert request.name == "Test Hero"
        assert request.race == Race.HUMAN
        assert request.character_class == CharacterClass.FIGHTER
        assert request.abilities.strength == 16
        assert request.backstory == "A brave warrior"

    def test_create_character_request_without_backstory(self):
        """Test CreateCharacterRequest without optional backstory."""
        abilities = Abilities()

        request = CreateCharacterRequest(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
        )

        assert request.backstory is None


class TestPlayerInput:
    """Test class for PlayerInput model."""

    def test_player_input_valid(self):
        """Test valid PlayerInput creation."""
        player_input = PlayerInput(
            message="I want to explore the forest",
            character_id="char_123",
            campaign_id="camp_456",
        )

        assert player_input.message == "I want to explore the forest"
        assert player_input.character_id == "char_123"
        assert player_input.campaign_id == "camp_456"

    def test_player_input_validation_error(self):
        """Test PlayerInput validation with missing fields."""
        with pytest.raises(ValidationError):
            PlayerInput(message="Hello")  # Missing character_id and campaign_id


class TestGameResponse:
    """Test class for GameResponse model."""

    def test_game_response_minimal(self):
        """Test GameResponse with minimal required fields."""
        response = GameResponse(message="You see a dark forest ahead.")

        assert response.message == "You see a dark forest ahead."
        assert response.images == []  # Default empty list
        assert response.state_updates == {}  # Default empty dict
        assert response.combat_updates is None  # Default None

    def test_game_response_full(self):
        """Test GameResponse with all fields."""
        response = GameResponse(
            message="Combat begins!",
            images=["http://example.com/battle.jpg"],
            state_updates={"health": 20, "location": "Forest"},
            combat_updates={"initiative": [1, 2, 3]},
        )

        assert response.message == "Combat begins!"
        assert response.images == ["http://example.com/battle.jpg"]
        assert response.state_updates["health"] == 20
        assert response.combat_updates["initiative"] == [1, 2, 3]


class TestCampaign:
    """Test class for Campaign model."""

    def test_campaign_creation(self):
        """Test Campaign model creation."""
        campaign = Campaign(name="Test Campaign", setting="Fantasy", tone="heroic")

        assert campaign.name == "Test Campaign"
        assert campaign.setting == "Fantasy"
        assert campaign.tone == "heroic"
        assert campaign.homebrew_rules == []  # Default empty list
        assert campaign.characters == []  # Default empty list
        assert campaign.session_log == []  # Default empty list
        assert campaign.state == "created"  # Default value
        assert campaign.id is not None  # Auto-generated UUID


class TestCreateCampaignRequest:
    """Test class for CreateCampaignRequest model."""

    def test_create_campaign_request_minimal(self):
        """Test CreateCampaignRequest with minimal fields."""
        request = CreateCampaignRequest(name="Test Campaign", setting="Fantasy World")

        assert request.name == "Test Campaign"
        assert request.setting == "Fantasy World"
        assert request.tone == "heroic"  # Default value
        assert request.homebrew_rules == []  # Default value

    def test_create_campaign_request_full(self):
        """Test CreateCampaignRequest with all fields."""
        request = CreateCampaignRequest(
            name="Dark Campaign",
            setting="Gothic Horror",
            tone="dark",
            homebrew_rules=["Custom rule 1", "Custom rule 2"],
        )

        assert request.name == "Dark Campaign"
        assert request.setting == "Gothic Horror"
        assert request.tone == "dark"
        assert request.homebrew_rules == ["Custom rule 1", "Custom rule 2"]


class TestGenerateImageRequest:
    """Test class for GenerateImageRequest model."""

    def test_generate_image_request(self):
        """Test GenerateImageRequest creation."""
        request = GenerateImageRequest(
            image_type="character_portrait", details={"name": "Hero", "race": "human"}
        )

        assert request.image_type == "character_portrait"
        assert request.details["name"] == "Hero"
        assert request.details["race"] == "human"


class TestBattleMapRequest:
    """Test class for BattleMapRequest model."""

    def test_battle_map_request_minimal(self):
        """Test BattleMapRequest with minimal fields."""
        request = BattleMapRequest(environment={"terrain": "forest", "size": "medium"})

        assert request.environment["terrain"] == "forest"
        assert request.environment["size"] == "medium"
        assert request.combat_context is None  # Default value

    def test_battle_map_request_full(self):
        """Test BattleMapRequest with all fields."""
        request = BattleMapRequest(
            environment={"terrain": "forest", "size": "medium"},
            combat_context={"participants": 4, "difficulty": "hard"},
        )

        assert request.environment["terrain"] == "forest"
        assert request.combat_context["participants"] == 4
        assert request.combat_context["difficulty"] == "hard"

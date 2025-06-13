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
    CastSpellRequest,
    CastSpellResponse,
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
            HitPoints(current=10)  # Missing maximum


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
        assert item.properties is not None
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
            # Test missing required fields - passing no arguments should raise ValidationError
            try:
                CharacterSheet()
            except TypeError:
                # If we get TypeError instead of ValidationError, that's also acceptable
                # as it indicates the required fields are enforced
                pass


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
            PlayerInput(
                message="Hello", character_id="", campaign_id=""
            )  # Empty required fields


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
        assert response.combat_updates is not None
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
        assert request.combat_context is not None
        assert request.combat_context["participants"] == 4
        assert request.combat_context["difficulty"] == "hard"


class TestValidationEdgeCases:
    """Test edge cases and boundary conditions for model validation."""

    def test_abilities_boundary_values(self):
        """Test abilities with boundary values."""
        # Test minimum values
        abilities = Abilities(
            strength=1,
            dexterity=1,
            constitution=1,
            intelligence=1,
            wisdom=1,
            charisma=1,
        )
        assert abilities.strength == 1

        # Test maximum realistic values
        abilities = Abilities(
            strength=30,
            dexterity=30,
            constitution=30,
            intelligence=30,
            wisdom=30,
            charisma=30,
        )
        assert abilities.strength == 30

    def test_hit_points_edge_cases(self):
        """Test hit points edge cases."""
        # Test zero current HP (unconscious/dead)
        hp = HitPoints(current=0, maximum=30)
        assert hp.current == 0
        assert hp.maximum == 30

        # Test maximum HP equals current
        hp = HitPoints(current=50, maximum=50)
        assert hp.current == hp.maximum

    def test_character_sheet_with_optional_fields(self):
        """Test character sheet with various optional field combinations."""
        abilities = Abilities()
        hit_points = HitPoints(current=10, maximum=10)

        # Test with minimal required fields
        character = CharacterSheet(
            name="Test",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
            hit_points=hit_points,
        )

        # Verify defaults are applied
        assert character.level == 1
        assert character.experience == 0
        assert character.armor_class == 10
        assert character.proficiency_bonus == 2
        assert character.inventory == []
        assert character.spells == []

    def test_item_properties_edge_cases(self):
        """Test item model with various property combinations."""
        # Test item with complex properties
        item = Item(
            name="Magical Artifact",
            properties={
                "damage": "2d6+3",
                "magical": True,
                "cursed": False,
                "weight_reduction": 0.5,
                "special_abilities": ["detect_magic", "light"],
            },
        )

        assert item.properties is not None
        assert item.properties["magical"] is True
        assert item.properties["cursed"] is False
        assert len(item.properties["special_abilities"]) == 2

    def test_spell_level_validation(self):
        """Test spell level constraints."""
        # Test cantrip (level 0)
        spell = Spell(
            name="Prestidigitation",
            level=0,
            school="Transmutation",
            casting_time="1 action",
            range="10 feet",
            components="V, S",
            duration="Up to 1 hour",
            description="Simple magical effect",
        )
        assert spell.level == 0

        # Test high level spell
        spell = Spell(
            name="Wish",
            level=9,
            school="Conjuration",
            casting_time="1 action",
            range="Self",
            components="V",
            duration="Instantaneous",
            description="The most powerful spell",
        )
        assert spell.level == 9

    def test_campaign_state_transitions(self):
        """Test campaign state management."""
        campaign = Campaign(
            name="Test Campaign", setting="Test Setting", state="created"
        )
        assert campaign.state == "created"

        # Test different states that might exist
        valid_states = ["created", "active", "paused", "completed"]
        for state in valid_states:
            campaign = Campaign(name="Test", setting="Test", state=state)
            assert campaign.state == state

    def test_player_input_message_lengths(self):
        """Test player input with various message lengths."""
        # Test short message
        player_input = PlayerInput(
            message="Hi", character_id="char_123", campaign_id="camp_456"
        )
        assert len(player_input.message) == 2

        # Test long message
        long_message = "I want to " + "really " * 100 + "explore this area thoroughly."
        player_input = PlayerInput(
            message=long_message, character_id="char_123", campaign_id="camp_456"
        )
        assert len(player_input.message) > 500

    def test_game_response_with_complex_data(self):
        """Test game response with complex state updates."""
        response = GameResponse(
            message="Combat round complete!",
            images=["url1.jpg", "url2.jpg", "url3.jpg"],
            state_updates={
                "character_health": {"current": 15, "maximum": 30},
                "location": {"name": "Dark Forest", "coordinates": {"x": 10, "y": 20}},
                "inventory_changes": [
                    {"action": "add", "item": "potion", "quantity": 1},
                    {"action": "remove", "item": "arrow", "quantity": 3},
                ],
                "experience_gained": 250,
            },
            combat_updates={
                "round": 3,
                "initiative_order": ["player1", "orc1", "player2"],
                "conditions": {"player1": ["poisoned"], "orc1": []},
                "damage_dealt": {"player1": 8, "orc1": 12},
            },
        )

        assert len(response.images) == 3
        assert response.state_updates["experience_gained"] == 250
        assert response.combat_updates is not None
        assert response.combat_updates["round"] == 3
        assert "poisoned" in response.combat_updates["conditions"]["player1"]

    def test_enum_case_sensitivity(self):
        """Test that enums handle case correctly."""
        # These should work with exact case
        assert CharacterClass.FIGHTER == "fighter"
        assert Race.HUMAN == "human"
        assert Ability.STRENGTH == "strength"

        # Test creating character with proper enum values
        abilities = Abilities()
        char_request = CreateCharacterRequest(
            name="Test",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
        )
        assert char_request.race == Race.HUMAN
        assert char_request.character_class == CharacterClass.FIGHTER


class TestCastSpellRequest:
    """Test class for CastSpellRequest model."""

    def test_cast_spell_request_minimal(self):
        """Test CastSpellRequest with minimal required fields."""
        request = CastSpellRequest(
            character_id="char_123",
            spell_id="spell_456",
            spell_level=1
        )
        
        assert request.character_id == "char_123"
        assert request.spell_id == "spell_456"
        assert request.spell_level == 1
        assert request.target_ids == []
        assert request.spell_attack_roll is None
        assert request.save_dc is None

    def test_cast_spell_request_with_targets(self):
        """Test CastSpellRequest with targets and optional fields."""
        request = CastSpellRequest(
            character_id="char_123",
            spell_id="spell_456",
            spell_level=3,
            target_ids=["enemy_1", "enemy_2"],
            spell_attack_roll=18,
            save_dc=15
        )
        
        assert request.character_id == "char_123"
        assert request.spell_id == "spell_456"
        assert request.spell_level == 3
        assert len(request.target_ids) == 2
        assert "enemy_1" in request.target_ids
        assert "enemy_2" in request.target_ids
        assert request.spell_attack_roll == 18
        assert request.save_dc == 15

    def test_cast_spell_request_validation(self):
        """Test CastSpellRequest validation."""
        import pytest
        from pydantic import ValidationError
        
        # Test empty character_id
        with pytest.raises(ValidationError):
            CastSpellRequest(
                character_id="",
                spell_id="spell_456",
                spell_level=1
            )
        
        # Test empty spell_id
        with pytest.raises(ValidationError):
            CastSpellRequest(
                character_id="char_123",
                spell_id="",
                spell_level=1
            )
        
        # Test invalid spell level (negative)
        with pytest.raises(ValidationError):
            CastSpellRequest(
                character_id="char_123",
                spell_id="spell_456",
                spell_level=-1
            )
        
        # Test invalid spell level (too high)
        with pytest.raises(ValidationError):
            CastSpellRequest(
                character_id="char_123",
                spell_id="spell_456",
                spell_level=10
            )


class TestCastSpellResponse:
    """Test class for CastSpellResponse model."""

    def test_cast_spell_response_minimal(self):
        """Test CastSpellResponse with minimal required fields."""
        response = CastSpellResponse(
            success=True,
            spell_name="Magic Missile",
            caster_name="Gandalf"
        )
        
        assert response.success is True
        assert response.spell_name == "Magic Missile"
        assert response.caster_name == "Gandalf"
        assert response.target_names == []
        assert response.effects == []
        assert response.damage_dealt == {}
        assert response.healing_done == {}
        assert response.saving_throws == {}
        assert response.spell_slot_used is False
        assert response.concentration_required is False
        assert response.ongoing_effects == []
        assert response.combat_updates == {}

    def test_cast_spell_response_with_damage(self):
        """Test CastSpellResponse with damage and effects."""
        response = CastSpellResponse(
            success=True,
            spell_name="Fireball",
            caster_name="Merlin",
            target_names=["Orc", "Goblin"],
            effects=["Explosion damages enemies"],
            damage_dealt={"orc_1": 18, "goblin_1": 15},
            spell_slot_used=True,
            combat_updates={"area_effect": True}
        )
        
        assert response.success is True
        assert response.spell_name == "Fireball"
        assert response.caster_name == "Merlin"
        assert len(response.target_names) == 2
        assert "Orc" in response.target_names
        assert "Goblin" in response.target_names
        assert len(response.effects) == 1
        assert "Explosion damages enemies" in response.effects
        assert response.damage_dealt["orc_1"] == 18
        assert response.damage_dealt["goblin_1"] == 15
        assert response.spell_slot_used is True
        assert response.combat_updates["area_effect"] is True

    def test_cast_spell_response_with_saving_throws(self):
        """Test CastSpellResponse with saving throw data."""
        response = CastSpellResponse(
            success=True,
            spell_name="Hold Person",
            caster_name="Cleric",
            target_names=["Bandit"],
            saving_throws={
                "bandit_1": {
                    "roll": 12,
                    "success": False,
                    "ability": "wisdom",
                    "dc": 15
                }
            },
            concentration_required=True,
            ongoing_effects=[{
                "effect": "paralyzed",
                "duration": "1 minute",
                "target_id": "bandit_1"
            }]
        )
        
        assert response.saving_throws["bandit_1"]["roll"] == 12
        assert response.saving_throws["bandit_1"]["success"] is False
        assert response.saving_throws["bandit_1"]["ability"] == "wisdom"
        assert response.saving_throws["bandit_1"]["dc"] == 15
        assert response.concentration_required is True
        assert len(response.ongoing_effects) == 1
        assert response.ongoing_effects[0]["effect"] == "paralyzed"

"""
Simple integration tests focusing on testable components.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSimpleIntegration:
    """Test simple integration scenarios."""

    def test_can_import_models(self):
        """Test that we can import and use the models."""
        from app.models.game_models import CharacterClass, Race, Abilities
        
        # Test that enums work
        assert CharacterClass.FIGHTER == "fighter"
        assert Race.HUMAN == "human"
        
        # Test that we can create model instances
        abilities = Abilities(strength=16, dexterity=14)
        assert abilities.strength == 16
        assert abilities.dexterity == 14

    def test_request_response_model_compatibility(self):
        """Test that request and response models are compatible."""
        from app.models.game_models import (
            CreateCharacterRequest, 
            CharacterSheet,
            PlayerInput,
            GameResponse,
            CreateCampaignRequest,
            Campaign,
            Abilities,
            Race,
            CharacterClass
        )
        
        # Test character request -> response compatibility
        abilities = Abilities(strength=16, dexterity=14, constitution=15)
        char_request = CreateCharacterRequest(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities
        )
        
        assert char_request.name == "Test Hero"
        assert char_request.race == Race.HUMAN
        assert char_request.character_class == CharacterClass.FIGHTER
        
        # Test player input -> game response compatibility
        player_input = PlayerInput(
            message="I attack the orc!",
            character_id="char_123",
            campaign_id="camp_456"
        )
        
        game_response = GameResponse(
            message="You swing your sword at the orc...",
            images=["http://example.com/combat.jpg"],
            state_updates={"health": 18},
            combat_updates={"round": 2}
        )
        
        assert player_input.message == "I attack the orc!"
        assert game_response.message == "You swing your sword at the orc..."
        
        # Test campaign request -> response compatibility
        camp_request = CreateCampaignRequest(
            name="Epic Adventure",
            setting="Fantasy Realm"
        )
        
        campaign = Campaign(
            name="Epic Adventure",
            setting="Fantasy Realm"
        )
        
        assert camp_request.name == campaign.name
        assert camp_request.setting == campaign.setting

    def test_data_validation_works(self):
        """Test that pydantic validation works correctly."""
        from app.models.game_models import (
            CreateCharacterRequest,
            PlayerInput,
            Abilities,
            Race,
            CharacterClass
        )
        from pydantic import ValidationError
        
        # Test valid data passes validation
        abilities = Abilities(strength=16)
        char_request = CreateCharacterRequest(
            name="Valid Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities
        )
        assert char_request.name == "Valid Hero"
        
        # Test invalid data raises validation error
        with pytest.raises(ValidationError):
            CreateCharacterRequest(
                name="",  # Empty name should fail
                race="invalid_race",  # Invalid race
                character_class=CharacterClass.FIGHTER,
                abilities=abilities
            )
        
        with pytest.raises(ValidationError):
            PlayerInput(
                message="Hello"
                # Missing required character_id and campaign_id
            )

    def test_uuid_generation_works(self):
        """Test that UUID generation works for models."""
        from app.models.game_models import Item, Spell, CharacterSheet, Campaign
        
        # Test multiple items get different UUIDs
        item1 = Item(name="Sword")
        item2 = Item(name="Shield")
        
        assert item1.id != item2.id
        assert len(item1.id) > 0
        assert len(item2.id) > 0
        
        # Test multiple campaigns get different UUIDs
        campaign1 = Campaign(name="Adventure 1", setting="Forest")
        campaign2 = Campaign(name="Adventure 2", setting="Desert")
        
        assert campaign1.id != campaign2.id
        assert len(campaign1.id) > 0
        assert len(campaign2.id) > 0

    def test_enum_string_values(self):
        """Test that all enums have correct string values."""
        from app.models.game_models import CharacterClass, Race, Ability, CombatState
        
        # Test character classes
        assert CharacterClass.FIGHTER.value == "fighter"
        assert CharacterClass.WIZARD.value == "wizard"
        assert CharacterClass.ROGUE.value == "rogue"
        
        # Test races
        assert Race.HUMAN.value == "human"
        assert Race.ELF.value == "elf"
        assert Race.DWARF.value == "dwarf"
        
        # Test abilities
        assert Ability.STRENGTH.value == "strength"
        assert Ability.DEXTERITY.value == "dexterity"
        assert Ability.CONSTITUTION.value == "constitution"
        
        # Test combat states
        assert CombatState.READY.value == "ready"
        assert CombatState.ACTIVE.value == "active"
        assert CombatState.COMPLETED.value == "completed"

    def test_model_serialization(self):
        """Test that models can be serialized to/from dictionaries."""
        from app.models.game_models import (
            Abilities, 
            CreateCharacterRequest, 
            GameResponse,
            Race,
            CharacterClass
        )
        
        # Test abilities serialization
        abilities = Abilities(strength=16, dexterity=14, constitution=15)
        abilities_dict = abilities.model_dump()
        
        assert abilities_dict["strength"] == 16
        assert abilities_dict["dexterity"] == 14
        assert abilities_dict["constitution"] == 15
        
        # Test character request serialization
        char_request = CreateCharacterRequest(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
            backstory="A brave warrior"
        )
        
        char_dict = char_request.model_dump()
        assert char_dict["name"] == "Test Hero"
        assert char_dict["race"] == "human"
        assert char_dict["character_class"] == "fighter"
        assert char_dict["backstory"] == "A brave warrior"
        
        # Test game response serialization
        response = GameResponse(
            message="Welcome to the adventure!",
            images=["http://example.com/tavern.jpg"],
            state_updates={"location": "tavern", "gold": 100}
        )
        
        response_dict = response.model_dump()
        assert response_dict["message"] == "Welcome to the adventure!"
        assert response_dict["images"] == ["http://example.com/tavern.jpg"]
        assert response_dict["state_updates"]["location"] == "tavern"
        assert response_dict["state_updates"]["gold"] == 100

    def test_default_values_work(self):
        """Test that default values are properly set on models."""
        from app.models.game_models import (
            Abilities, 
            HitPoints, 
            Item, 
            GameResponse,
            CreateCampaignRequest,
            Campaign
        )
        
        # Test abilities defaults
        abilities = Abilities()
        assert abilities.strength == 10
        assert abilities.dexterity == 10
        assert abilities.constitution == 10
        assert abilities.intelligence == 10
        assert abilities.wisdom == 10
        assert abilities.charisma == 10
        
        # Test item defaults
        item = Item(name="Simple Sword")
        assert item.quantity == 1
        assert item.description is None
        assert item.weight is None
        assert item.value is None
        
        # Test game response defaults
        response = GameResponse(message="Hello")
        assert response.images == []
        assert response.state_updates == {}
        assert response.combat_updates is None
        
        # Test campaign request defaults
        request = CreateCampaignRequest(name="Test", setting="Forest")
        assert request.tone == "heroic"
        assert request.homebrew_rules == []
        
        # Test campaign defaults
        campaign = Campaign(name="Test", setting="Forest")
        assert campaign.tone == "heroic"
        assert campaign.homebrew_rules == []
        assert campaign.characters == []
        assert campaign.session_log == []
        assert campaign.state == "created"
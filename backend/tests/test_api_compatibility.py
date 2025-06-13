"""
API integration tests to verify frontend-backend compatibility.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.game_models import (
    CharacterSheet,
    CreateCharacterRequest,
    PlayerInput,
    GameResponse,
    Campaign,
    CreateCampaignRequest,
    Race,
    CharacterClass,
    Abilities
)


class TestAPICompatibility:
    """Test API compatibility between frontend and backend."""

    def test_character_creation_compatibility(self):
        """Test that character creation request/response models are compatible."""
        # Test frontend request format
        frontend_request = {
            "name": "Test Hero",
            "race": "human",
            "character_class": "fighter",
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10
            },
            "backstory": "A brave warrior"
        }
        
        # Validate backend can parse the request
        abilities = Abilities(**frontend_request["abilities"])
        char_request = CreateCharacterRequest(
            name=frontend_request["name"],
            race=Race(frontend_request["race"]),
            character_class=CharacterClass(frontend_request["character_class"]),
            abilities=abilities,
            backstory=frontend_request.get("backstory")
        )
        
        assert char_request.name == "Test Hero"
        assert char_request.race == Race.HUMAN
        assert char_request.character_class == CharacterClass.FIGHTER
        
        # Test backend response format matches frontend expectations
        character_sheet = CharacterSheet(
            name=char_request.name,
            race=char_request.race,
            character_class=char_request.character_class,
            abilities=char_request.abilities,
            hit_points={"current": 20, "maximum": 20}
        )
        
        # Convert to dict to simulate API response
        response_dict = character_sheet.dict()
        
        # Frontend expects these fields
        expected_fields = {
            "id", "name", "race", "character_class", "level", 
            "abilities", "hit_points", "inventory"
        }
        
        for field in expected_fields:
            assert field in response_dict, f"Missing field {field} in response"
        
        # Check abilities structure
        assert "strength" in response_dict["abilities"]
        assert "dexterity" in response_dict["abilities"]
        assert "constitution" in response_dict["abilities"]
        assert "intelligence" in response_dict["abilities"]
        assert "wisdom" in response_dict["abilities"]
        assert "charisma" in response_dict["abilities"]
        
        # Check hit_points structure
        assert "current" in response_dict["hit_points"]
        assert "maximum" in response_dict["hit_points"]

    def test_campaign_creation_compatibility(self):
        """Test that campaign creation request/response models are compatible."""
        # Test frontend request format
        frontend_request = {
            "name": "Epic Adventure",
            "setting": "Fantasy Realm",
            "tone": "heroic",
            "homebrew_rules": ["Custom rule 1", "Custom rule 2"]
        }
        
        # Validate backend can parse the request
        campaign_request = CreateCampaignRequest(**frontend_request)
        
        assert campaign_request.name == "Epic Adventure"
        assert campaign_request.setting == "Fantasy Realm"
        assert campaign_request.tone == "heroic"
        assert len(campaign_request.homebrew_rules) == 2
        
        # Test backend response format
        campaign = Campaign(
            name=campaign_request.name,
            setting=campaign_request.setting,
            tone=campaign_request.tone,
            homebrew_rules=campaign_request.homebrew_rules
        )
        
        response_dict = campaign.dict()
        
        # Frontend expects these fields
        expected_fields = {
            "id", "name", "setting", "tone", "homebrew_rules", 
            "characters", "session_log", "state"
        }
        
        for field in expected_fields:
            assert field in response_dict, f"Missing field {field} in campaign response"

    def test_player_input_compatibility(self):
        """Test that player input request/response models are compatible."""
        # Test frontend request format
        frontend_request = {
            "message": "I attack the orc!",
            "character_id": "char_123",
            "campaign_id": "camp_456"
        }
        
        # Validate backend can parse the request
        player_input = PlayerInput(**frontend_request)
        
        assert player_input.message == "I attack the orc!"
        assert player_input.character_id == "char_123"
        assert player_input.campaign_id == "camp_456"
        
        # Test backend response format
        game_response = GameResponse(
            message="You swing your sword at the orc...",
            images=["http://example.com/combat.jpg"],
            state_updates={"health": 18},
            combat_updates={
                "status": "active",
                "map_url": "http://example.com/battle-map.jpg"
            }
        )
        
        response_dict = game_response.dict()
        
        # Frontend expects these fields
        expected_fields = {"message", "images", "state_updates", "combat_updates"}
        
        for field in expected_fields:
            assert field in response_dict, f"Missing field {field} in game response"
        
        # Check combat_updates structure if present
        if response_dict["combat_updates"]:
            assert "status" in response_dict["combat_updates"]

    def test_field_naming_consistency(self):
        """Test that field naming is consistent between frontend and backend."""
        # Create a character to test field names
        character = CharacterSheet(
            name="Test Character",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=Abilities(strength=16, dexterity=14, constitution=15),
            hit_points={"current": 20, "maximum": 20}
        )
        
        char_dict = character.dict()
        
        # These are the critical field mappings frontend expects
        critical_fields = {
            "character_class": "character_class",  # NOT "class"
            "hit_points": "hit_points",  # NOT "hitPoints"
            "abilities": "abilities"
        }
        
        for backend_field, expected_field in critical_fields.items():
            assert backend_field in char_dict, f"Backend missing field {backend_field}"
            assert backend_field == expected_field, f"Field naming mismatch: {backend_field} != {expected_field}"
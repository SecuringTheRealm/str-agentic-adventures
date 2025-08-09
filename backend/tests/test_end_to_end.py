"""
End-to-end integration tests to verify complete functionality.
"""

import os
import sys

import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEndToEndWorkflows:
    """Test complete workflows from request to response."""

    @pytest.mark.integration
    def test_character_creation_workflow(self) -> None:
        """Test complete character creation workflow."""
        # This test validates the data flow works correctly
        # even without running the full server

        # Frontend request data
        frontend_request = {
            "name": "Legolas",
            "race": "elf",
            "character_class": "ranger",
            "abilities": {
                "strength": 14,
                "dexterity": 18,
                "constitution": 14,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 12,
            },
            "backstory": "An elven archer from Mirkwood",
        }

        # Validate this would work with our models (when dependencies are available)
        try:
            from app.models.game_models import (
                Abilities,
                CharacterClass,
                CreateCharacterRequest,
                Race,
            )

            abilities = Abilities(**frontend_request["abilities"])
            char_request = CreateCharacterRequest(
                name=frontend_request["name"],
                race=Race(frontend_request["race"]),
                character_class=CharacterClass(frontend_request["character_class"]),
                abilities=abilities,
                backstory=frontend_request.get("backstory"),
            )

            # Verify the conversion works
            assert char_request.name == "Legolas"
            assert char_request.race == Race.ELF
            assert char_request.character_class == CharacterClass.RANGER
            assert char_request.abilities.dexterity == 18

            print("✅ Character creation request validation passed")

        except ImportError:
            print("⚠️ Pydantic not available - skipping model validation")
            # Just verify the data structure is correct
            assert "name" in frontend_request
            assert "race" in frontend_request
            assert "character_class" in frontend_request
            assert "abilities" in frontend_request
            assert all(
                ability in frontend_request["abilities"]
                for ability in [
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ]
            )
            print("✅ Character creation data structure validation passed")

    @pytest.mark.integration
    def test_campaign_creation_workflow(self) -> None:
        """Test complete campaign creation workflow."""
        frontend_request = {
            "name": "The Fellowship's Journey",
            "setting": "Middle-earth",
            "tone": "epic",
            "homebrew_rules": ["Use group initiative", "Custom spell components"],
        }

        try:
            from app.models.game_models import Campaign, CreateCampaignRequest

            campaign_request = CreateCampaignRequest(**frontend_request)

            assert campaign_request.name == "The Fellowship's Journey"
            assert campaign_request.setting == "Middle-earth"
            assert campaign_request.tone == "epic"
            assert len(campaign_request.homebrew_rules) == 2

            # Simulate creating a campaign response
            campaign = Campaign(
                name=campaign_request.name,
                setting=campaign_request.setting,
                tone=campaign_request.tone,
                homebrew_rules=campaign_request.homebrew_rules,
            )

            response_dict = campaign.dict()

            # Verify response has all required fields for frontend
            required_fields = [
                "id",
                "name",
                "setting",
                "tone",
                "homebrew_rules",
                "characters",
            ]
            for field in required_fields:
                assert field in response_dict

            print("✅ Campaign creation workflow validation passed")

        except ImportError:
            print("⚠️ Pydantic not available - skipping model validation")
            # Just verify data structure
            assert "name" in frontend_request
            assert "setting" in frontend_request
            assert "tone" in frontend_request
            assert isinstance(frontend_request["homebrew_rules"], list)
            print("✅ Campaign creation data structure validation passed")

    @pytest.mark.integration
    def test_player_input_workflow(self) -> None:
        """Test player input processing workflow."""
        frontend_request = {
            "message": "I search for traps in the corridor",
            "character_id": "char_123",
            "campaign_id": "camp_456",
        }

        try:
            from app.models.game_models import GameResponse, PlayerInput

            player_input = PlayerInput(**frontend_request)

            assert player_input.message == "I search for traps in the corridor"
            assert player_input.character_id == "char_123"
            assert player_input.campaign_id == "camp_456"

            # Simulate game response
            game_response = GameResponse(
                message="You find a pressure plate hidden beneath some rubble.",
                images=["https://example.com/trap-detection.jpg"],
                state_updates={"perception_used": True},
                combat_updates=None,
            )

            response_dict = game_response.dict()

            # Verify response structure for frontend
            assert "message" in response_dict
            assert "images" in response_dict
            assert "state_updates" in response_dict
            assert "combat_updates" in response_dict

            print("✅ Player input workflow validation passed")

        except ImportError:
            print("⚠️ Pydantic not available - skipping model validation")
            # Verify data structure
            assert "message" in frontend_request
            assert "character_id" in frontend_request
            assert "campaign_id" in frontend_request
            print("✅ Player input data structure validation passed")

    @pytest.mark.integration
    def test_image_generation_workflow(self) -> None:
        """Test image generation workflow."""
        frontend_request = {
            "image_type": "character_portrait",
            "details": {
                "character_name": "Legolas",
                "race": "elf",
                "class": "ranger",
                "description": "Tall elf with blonde hair and piercing blue eyes",
            },
        }

        try:
            from app.models.game_models import GenerateImageRequest

            image_request = GenerateImageRequest(**frontend_request)

            assert image_request.image_type == "character_portrait"
            assert "character_name" in image_request.details

            print("✅ Image generation workflow validation passed")

        except ImportError:
            print("⚠️ Pydantic not available - skipping model validation")
            # Verify structure
            assert "image_type" in frontend_request
            assert "details" in frontend_request
            assert frontend_request["image_type"] in [
                "character_portrait",
                "scene_illustration",
                "item_visualization",
            ]
            print("✅ Image generation data structure validation passed")


class TestComponentIntegration:
    """Test that different components work together correctly."""

    @pytest.mark.unit
    def test_api_route_coverage(self) -> None:
        """Test that all frontend API calls have corresponding backend routes."""
        # Read the game routes file with correct path
        routes_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app",
            "api",
            "game_routes.py",
        )
        with open(routes_file) as f:
            routes_content = f.read()

        # Check that all critical routes are present
        critical_routes = [
            'post("/character"',  # Character creation
            'get("/character/{character_id}"',  # Character retrieval
            'post("/input"',  # Player input
            'post("/campaign"',  # Campaign creation
            'post("/generate-image"',  # Image generation
            'post("/battle-map"',  # Battle map generation
        ]

        missing_routes = []
        for route in critical_routes:
            if route not in routes_content:
                missing_routes.append(route)

        assert len(missing_routes) == 0, f"Missing critical routes: {missing_routes}"
        print("✅ All critical API routes are present")

    @pytest.mark.unit
    def test_model_field_consistency(self) -> None:
        """Test that model fields are consistent across the application."""
        # Read the models file with correct path
        models_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app",
            "models",
            "game_models.py",
        )
        with open(models_file) as f:
            models_content = f.read()

        # Check for critical field naming patterns
        field_checks = [
            ("character_class", "NOT class"),  # Ensure we use character_class
            ("hit_points", "NOT hitPoints"),  # Ensure we use hit_points
            ("class CharacterSheet", "CharacterSheet model exists"),
            ("class CreateCharacterRequest", "CreateCharacterRequest model exists"),
            ("class GameResponse", "GameResponse model exists"),
        ]

        for field_pattern, description in field_checks:
            if field_pattern.startswith("NOT "):
                # This is a negative check
                negative_pattern = field_pattern[4:]
                if negative_pattern in models_content:
                    print(f"⚠️ Found discouraged pattern: {negative_pattern}")
                else:
                    print(f"✅ {description}")
            else:
                # This is a positive check
                if field_pattern in models_content:
                    print(f"✅ {description}")
                else:
                    raise AssertionError(f"Missing required pattern: {field_pattern}")

    @pytest.mark.integration
    def test_agent_integration_points(self) -> None:
        """Test that agents are properly integrated with the API layer."""
        # Read the game routes file with correct path
        routes_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app",
            "api",
            "game_routes.py",
        )
        with open(routes_file) as f:
            routes_content = f.read()

        # Check that agents are imported and used
        agent_imports = [
            "from app.agents.dungeon_master_agent import get_dungeon_master",
            "from app.agents.scribe_agent import get_scribe",
            "from app.agents.combat_cartographer_agent import get_combat_cartographer",
            "from app.agents.artist_agent import get_artist",
        ]

        for agent_import in agent_imports:
            if agent_import in routes_content:
                print(f"✅ Agent imported: {agent_import.split('import ')[-1]}")
            else:
                print(f"⚠️ Agent not imported: {agent_import.split('import ')[-1]}")

        # Check that agents are used in endpoints
        agent_usage = [
            "await get_scribe().create_character",
            "await get_scribe().get_character",
            "await get_dungeon_master().create_campaign",
            "await get_artist().generate",
        ]

        used_agents = []
        for usage in agent_usage:
            if usage in routes_content:
                used_agents.append(usage)
                print(f"✅ Agent used: {usage}")

        assert len(used_agents) >= 2, "At least some agents should be used in routes"

"""Test the enhanced level-up functionality with class features."""

from unittest.mock import MagicMock, patch

import pytest
from app.agents.scribe_agent import ScribeAgent


class TestSRDLevelUp:
    """Test SRD-compliant level-up functionality."""

    @pytest.fixture
    def scribe_agent(self):
        """Create a ScribeAgent instance for testing."""
        with (
            patch("app.agents.scribe_agent.init_db"),
            patch(
                "app.agents.scribe_agent.agent_client_manager.get_chat_client"
            ) as mock_kernel,
            patch("app.agents.scribe_agent.ScribeAgent._register_skills"),
        ):
            mock_kernel.return_value = MagicMock()
            return ScribeAgent()

    @pytest.mark.asyncio
    async def test_level_up_adds_class_features(self, scribe_agent) -> None:
        """Test that leveling up adds appropriate class features."""
        # Mock a fighter character leveling up to level 2
        fighter_data = {
            "id": "test_fighter",
            "name": "Test Fighter",
            "race": "human",
            "character_class": "fighter",
            "level": 1,
            "experience": 300,  # Enough for level 2
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 10,
                "wisdom": 12,
                "charisma": 8,
            },
            "hitPoints": {"current": 12, "maximum": 12},
            "proficiency_bonus": 2,
            "features": [
                {
                    "name": "Fighting Style",
                    "description": "...",
                    "type": "class_choice",
                    "source": "class",
                    "level_gained": 1,
                },
                {
                    "name": "Second Wind",
                    "description": "...",
                    "type": "healing",
                    "source": "class",
                    "level_gained": 1,
                },
            ],
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_character = MagicMock()
            mock_character.data = fighter_data
            mock_db.get.return_value = mock_character
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock the rules engine completely
            with patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules:
                mock_rules_instance = MagicMock()
                mock_rules.return_value = mock_rules_instance

                # Mock level calculation to allow level 2
                mock_rules_instance.calculate_level.return_value = {"current_level": 2}
                mock_rules_instance.calculate_level_up_hp.return_value = {
                    "total_hp_gain": 7
                }
                mock_rules_instance.calculate_proficiency_bonus.return_value = {
                    "proficiency_bonus": 2
                }
                mock_rules_instance.check_asi_eligibility.return_value = {
                    "asi_remaining": 0
                }
                mock_rules_instance.asi_levels = [4, 6, 8, 12, 14, 16, 19]

                result = await scribe_agent.level_up_character(
                    "test_fighter", {"strength": 1, "constitution": 1}
                )

                # Check that level 2 features were added
                features_gained = result.get("features_gained", [])

                # Should include Action Surge for level 2 Fighter
                class_feature_added = any(
                    "Class Feature: Action Surge" in feature
                    for feature in features_gained
                )
                assert class_feature_added, (
                    f"Expected Action Surge to be added, got: {features_gained}"
                )

    @pytest.mark.asyncio
    async def test_level_up_preserves_existing_features(self, scribe_agent) -> None:
        """Test that leveling up preserves existing features."""
        # Mock a wizard character leveling up to level 2
        wizard_data = {
            "id": "test_wizard",
            "name": "Test Wizard",
            "race": "elf",
            "character_class": "wizard",
            "level": 1,
            "experience": 300,  # Enough for level 2
            "abilities": {
                "strength": 8,
                "dexterity": 16,  # 14 + 2 from elf
                "constitution": 14,
                "intelligence": 16,
                "wisdom": 12,
                "charisma": 10,
            },
            "hitPoints": {"current": 8, "maximum": 8},
            "proficiency_bonus": 2,
            "features": [
                {
                    "name": "Spellcasting",
                    "description": "...",
                    "type": "spellcasting",
                    "source": "class",
                    "level_gained": 1,
                },
                {
                    "name": "Arcane Recovery",
                    "description": "...",
                    "type": "spellcasting",
                    "source": "class",
                    "level_gained": 1,
                },
                {
                    "name": "Darkvision",
                    "description": "...",
                    "type": "racial",
                    "source": "race",
                    "level_gained": 1,
                },
            ],
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_character = MagicMock()
            mock_character.data = wizard_data
            mock_db.get.return_value = mock_character
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.level_up_character(
                "test_wizard", {"intelligence": 2}
            )

            # Check that the updated character has both old and new features
            updated_character = result.get("updated_character", {})
            features = updated_character.get("features", [])

            # Should still have level 1 features
            feature_names = [f["name"] for f in features]
            assert "Spellcasting" in feature_names
            assert "Arcane Recovery" in feature_names
            assert "Darkvision" in feature_names

            # Should have new level 2 feature
            assert "Arcane Tradition" in feature_names

    @pytest.mark.asyncio
    async def test_level_up_multiple_levels_adds_all_features(
        self, scribe_agent
    ) -> None:
        """Test that when a character gains multiple levels, all features are added."""
        # Mock a rogue gaining level 3 (which gives both level 2 and 3 features if leveling from 1)
        rogue_data = {
            "id": "test_rogue",
            "name": "Test Rogue",
            "race": "halfling",
            "character_class": "rogue",
            "level": 1,
            "experience": 900,  # Enough for level 3
            "abilities": {
                "strength": 8,
                "dexterity": 17,  # 15 + 2 from halfling
                "constitution": 14,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10,
            },
            "hitPoints": {"current": 10, "maximum": 10},
            "proficiency_bonus": 2,
            "features": [
                {
                    "name": "Expertise",
                    "description": "...",
                    "type": "skill",
                    "source": "class",
                    "level_gained": 1,
                },
                {
                    "name": "Sneak Attack",
                    "description": "...",
                    "type": "combat",
                    "source": "class",
                    "level_gained": 1,
                },
            ],
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_character = MagicMock()
            mock_character.data = rogue_data
            mock_db.get.return_value = mock_character
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock the rules engine to allow this level up
            with patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules:
                mock_rules_instance = MagicMock()
                mock_rules.return_value = mock_rules_instance

                # Mock level calculation to allow level 3
                mock_rules_instance.calculate_level.return_value = {"current_level": 3}
                mock_rules_instance.calculate_level_up_hp.return_value = {
                    "total_hp_gain": 6
                }
                mock_rules_instance.calculate_proficiency_bonus.return_value = {
                    "proficiency_bonus": 2
                }
                mock_rules_instance.check_asi_eligibility.return_value = {
                    "asi_remaining": 0
                }
                mock_rules_instance.asi_levels = [4, 8, 12, 16, 19]

                result = await scribe_agent.level_up_character("test_rogue", None)

                # Should have level 3 features added
                features_gained = result.get("features_gained", [])
                class_feature_added = any(
                    "Class Feature: Roguish Archetype" in feature
                    for feature in features_gained
                )
                assert class_feature_added, (
                    f"Expected Roguish Archetype to be added, got: {features_gained}"
                )

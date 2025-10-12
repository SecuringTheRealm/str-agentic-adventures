"""Integration test demonstrating complete SRD-compliant character creation."""

from unittest.mock import MagicMock, patch

import pytest
from app.agents.scribe_agent import ScribeAgent


class TestSRDIntegration:
    """Integration tests for SRD compliance improvements."""

    @pytest.fixture
    def scribe_agent(self):
        """Create a ScribeAgent instance for testing."""
        with (
            patch("app.agents.scribe_agent.init_db"),
            patch(
                "app.agents.scribe_agent.kernel_manager.create_kernel"
            ) as mock_kernel,
            patch("app.agents.scribe_agent.ScribeAgent._register_skills"),
        ):
            mock_kernel.return_value = MagicMock()
            return ScribeAgent()

    @pytest.mark.asyncio
    async def test_complete_character_creation_with_srd_features(
        self, scribe_agent
    ) -> None:
        """Test complete character creation with all SRD features applied."""
        # Create a comprehensive character with race, class, and background
        character_data = {
            "name": "Thorin Ironforge",
            "race": "dwarf",
            "class": "fighter",
            "background": "soldier",
            "strength": 16,
            "dexterity": 12,
            "constitution": 16,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 8,
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(character_data)

            # Verify basic character info
            assert result["name"] == "Thorin Ironforge"
            assert result["race"] == "dwarf"
            assert result["character_class"] == "fighter"
            assert result["background"] == "soldier"

            # Verify racial bonuses applied (Dwarf gets +2 CON)
            abilities = result["abilities"]
            assert abilities["constitution"] == 18  # 16 + 2 from dwarf
            assert abilities["strength"] == 16  # No racial bonus

            # Verify racial speed (Dwarves have 25 ft speed)
            assert result["speed"] == 25

            # Verify class features
            features = result.get("features", [])
            feature_names = [f["name"] for f in features]

            # Fighter level 1 features
            assert "Fighting Style" in feature_names
            assert "Second Wind" in feature_names

            # Dwarf racial traits
            assert "Darkvision" in feature_names
            assert "Dwarven Resilience" in feature_names
            assert "Dwarven Combat Training" in feature_names
            assert "Stonecunning" in feature_names

            # Soldier background feature
            assert "Military Rank" in feature_names

            # Verify class saving throw proficiencies (Fighter: STR, CON)
            saving_throws = result.get("saving_throw_proficiencies", [])
            assert "strength" in saving_throws
            assert "constitution" in saving_throws

            # Verify background skill proficiencies (Soldier: athletics, intimidation)
            skills = result.get("skills", {})
            assert skills.get("athletics") is True
            assert skills.get("intimidation") is True

            # Verify proper HP calculation (Fighter d10 + CON modifier)
            # d10 max (10) + CON modifier (+4 from 18 CON) = 14
            expected_hp = 10 + 4
            assert result["hit_points"]["maximum"] == expected_hp
            assert result["hit_points"]["current"] == expected_hp

            # Verify hit dice is set correctly
            assert result["hit_dice"] == "1d10"

            # Print summary for visual verification
            print("\n=== Character Creation Summary ===")
            print(f"Name: {result['name']}")
            print(f"Race: {result['race'].title()}")
            print(f"Class: {result['character_class'].title()}")
            print(f"Background: {result['background'].title()}")
            print(f"Speed: {result['speed']} ft")
            print(
                f"HP: {result['hit_points']['current']}/{result['hit_points']['maximum']}"
            )
            print(
                f"Abilities: STR {abilities['strength']}, DEX {abilities['dexterity']}, CON {abilities['constitution']}"
            )
            print(f"Features: {len(features)} total")
            print(f"Skills: {list(skills.keys())}")
            print(f"Saving Throws: {saving_throws}")

    @pytest.mark.asyncio
    async def test_spellcaster_creation_with_srd_features(self, scribe_agent) -> None:
        """Test creating a spellcaster with proper SRD compliance."""
        # Create an Elf Wizard with Sage background
        character_data = {
            "name": "Elaria Starweaver",
            "race": "elf",
            "class": "wizard",
            "background": "sage",
            "strength": 8,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 10,
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(character_data)

            # Verify racial bonuses (Elf gets +2 DEX)
            abilities = result["abilities"]
            assert abilities["dexterity"] == 16  # 14 + 2 from elf
            assert abilities["intelligence"] == 16  # No racial bonus

            # Verify racial speed (Elves have 30 ft speed)
            assert result["speed"] == 30

            # Verify wizard features
            features = result.get("features", [])
            feature_names = [f["name"] for f in features]

            # Wizard level 1 features
            assert "Spellcasting" in feature_names
            assert "Arcane Recovery" in feature_names

            # Elf racial traits
            assert "Darkvision" in feature_names
            assert "Keen Senses" in feature_names
            assert "Fey Ancestry" in feature_names
            assert "Trance" in feature_names

            # Sage background feature
            assert "Researcher" in feature_names

            # Verify wizard saving throws (INT, WIS)
            saving_throws = result.get("saving_throw_proficiencies", [])
            assert "intelligence" in saving_throws
            assert "wisdom" in saving_throws

            # Verify sage skills (arcana, history)
            skills = result.get("skills", {})
            assert skills.get("arcana") is True
            assert skills.get("history") is True

            # Verify wizard hit die and HP calculation
            assert result["hit_dice"] == "1d6"
            # d6 max (6) + CON modifier (+1 from 13 CON) = 7
            expected_hp = 6 + 1
            assert result["hit_points"]["maximum"] == expected_hp

"""Test the enhanced character creation with SRD compliance features."""

from unittest.mock import MagicMock, patch

import pytest
from app.agents.scribe_agent import ScribeAgent


class TestSRDCharacterCreation:
    """Test SRD-compliant character creation features."""

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
            agent = ScribeAgent()
            return agent

    @pytest.mark.asyncio
    async def test_character_creation_applies_racial_bonuses(self, scribe_agent):
        """Test that character creation applies racial ability bonuses."""
        character_data = {
            "name": "Test Elf",
            "race": "elf",
            "class": "wizard",
            "strength": 10,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 15,
            "wisdom": 13,
            "charisma": 8,
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(character_data)

            # Check that racial bonuses were applied (Elf gets +2 DEX)
            assert result["abilities"]["dexterity"] == 14  # 12 + 2
            assert result["abilities"]["strength"] == 10  # No change
            assert result["race"] == "elf"
            assert result["speed"] == 30  # Elf speed

    @pytest.mark.asyncio
    async def test_character_creation_sets_correct_speed(self, scribe_agent):
        """Test that character creation sets racial speed correctly."""
        dwarf_data = {"name": "Test Dwarf", "race": "dwarf", "class": "fighter"}

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(dwarf_data)

            # Dwarves have 25 ft speed
            assert result["speed"] == 25

    @pytest.mark.asyncio
    async def test_character_creation_adds_class_features(self, scribe_agent):
        """Test that character creation adds level 1 class features."""
        fighter_data = {"name": "Test Fighter", "race": "human", "class": "fighter"}

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(fighter_data)

            # Check that Fighter level 1 features were added
            features = result.get("features", [])
            feature_names = [f["name"] for f in features]

            assert "Fighting Style" in feature_names
            assert "Second Wind" in feature_names

    @pytest.mark.asyncio
    async def test_character_creation_adds_racial_traits(self, scribe_agent):
        """Test that character creation adds racial traits as features."""
        elf_data = {"name": "Test Elf", "race": "elf", "class": "rogue"}

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(elf_data)

            # Check that Elf racial traits were added
            features = result.get("features", [])
            feature_names = [f["name"] for f in features]

            assert "Darkvision" in feature_names
            assert "Keen Senses" in feature_names
            assert "Fey Ancestry" in feature_names

    @pytest.mark.asyncio
    async def test_character_creation_sets_saving_throws(self, scribe_agent):
        """Test that character creation sets class saving throw proficiencies."""
        wizard_data = {"name": "Test Wizard", "race": "human", "class": "wizard"}

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(wizard_data)

            # Wizard should have Intelligence and Wisdom saving throw proficiencies
            saving_throws = result.get("saving_throw_proficiencies", [])
            assert "intelligence" in saving_throws
            assert "wisdom" in saving_throws

    @pytest.mark.asyncio
    async def test_character_creation_calculates_hp_correctly(self, scribe_agent):
        """Test that character creation calculates initial HP correctly."""
        barbarian_data = {
            "name": "Test Barbarian",
            "race": "half-orc",
            "class": "barbarian",
            "constitution": 16,  # +3 modifier
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(barbarian_data)

            # Barbarian gets d12 hit die (max 12) + CON modifier
            # Half-orc gets +1 CON, so final CON is 17 (+3 modifier)
            expected_hp = 12 + 3  # 15
            assert result["hit_points"]["maximum"] == expected_hp
            assert result["hit_points"]["current"] == expected_hp

    @pytest.mark.asyncio
    async def test_character_creation_applies_background(self, scribe_agent):
        """Test that character creation applies background skill proficiencies."""
        acolyte_data = {
            "name": "Test Acolyte",
            "race": "human",
            "class": "cleric",
            "background": "acolyte",
        }

        with patch("app.agents.scribe_agent.get_session") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            result = await scribe_agent.create_character(acolyte_data)

            # Check that background was applied
            assert result["background"] == "acolyte"

            # Check that background skills were added
            skills = result.get("skills", {})
            assert skills.get("insight") is True
            assert skills.get("religion") is True

            # Check that background feature was added
            features = result.get("features", [])
            feature_names = [f["name"] for f in features]
            assert "Shelter of the Faithful" in feature_names

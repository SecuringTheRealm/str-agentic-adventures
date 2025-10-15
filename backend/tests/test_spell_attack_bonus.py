"""
Test spell attack bonus endpoint.
"""

import os
import sys

from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSpellAttackBonusEndpoint:
    """Test the spell attack bonus calculation endpoint."""

    def test_spell_attack_bonus_valid_wizard(self) -> None:
        """Test spell attack bonus calculation for a wizard."""
        from app.main import app

        client = TestClient(app)

        # Test wizard (intelligence-based spellcaster)
        request_data = {
            "character_class": "wizard",
            "level": 5,
            "spellcasting_ability_score": 16,  # +3 modifier
        }

        response = client.post("/game/spells/attack-bonus", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["character_class"] == "wizard"
        assert data["level"] == 5
        assert data["spellcasting_ability"] == "intelligence"
        assert data["spellcasting_ability_score"] == 16
        assert data["ability_modifier"] == 3  # (16-10)//2 = 3
        assert data["proficiency_bonus"] == 3  # Level 5 = +3 proficiency
        assert data["spell_attack_bonus"] == 6  # 3 + 3 = 6

    def test_spell_attack_bonus_valid_cleric(self) -> None:
        """Test spell attack bonus calculation for a cleric."""
        from app.main import app

        client = TestClient(app)

        # Test cleric (wisdom-based spellcaster)
        request_data = {
            "character_class": "cleric",
            "level": 1,
            "spellcasting_ability_score": 14,  # +2 modifier
        }

        response = client.post("/game/spells/attack-bonus", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["character_class"] == "cleric"
        assert data["level"] == 1
        assert data["spellcasting_ability"] == "wisdom"
        assert data["spellcasting_ability_score"] == 14
        assert data["ability_modifier"] == 2  # (14-10)//2 = 2
        assert data["proficiency_bonus"] == 2  # Level 1 = +2 proficiency
        assert data["spell_attack_bonus"] == 4  # 2 + 2 = 4

    def test_spell_attack_bonus_valid_sorcerer(self) -> None:
        """Test spell attack bonus calculation for a sorcerer."""
        from app.main import app

        client = TestClient(app)

        # Test sorcerer (charisma-based spellcaster)
        request_data = {
            "character_class": "sorcerer",
            "level": 17,
            "spellcasting_ability_score": 20,  # +5 modifier
        }

        response = client.post("/game/spells/attack-bonus", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["character_class"] == "sorcerer"
        assert data["level"] == 17
        assert data["spellcasting_ability"] == "charisma"
        assert data["spellcasting_ability_score"] == 20
        assert data["ability_modifier"] == 5  # (20-10)//2 = 5
        assert data["proficiency_bonus"] == 6  # Level 17 = +6 proficiency
        assert data["spell_attack_bonus"] == 11  # 5 + 6 = 11

    def test_spell_attack_bonus_invalid_class(self) -> None:
        """Test spell attack bonus with non-spellcasting class."""
        from app.main import app

        client = TestClient(app)

        # Test fighter (not a spellcasting class)
        request_data = {
            "character_class": "fighter",
            "level": 5,
            "spellcasting_ability_score": 16,
        }

        response = client.post("/game/spells/attack-bonus", json=request_data)
        assert response.status_code == 400
        assert "not a spellcasting class" in response.json()["detail"]

    def test_spell_attack_bonus_invalid_request(self) -> None:
        """Test spell attack bonus with invalid request data."""
        from app.main import app

        client = TestClient(app)

        # Test missing required fields
        invalid_requests = [
            {},  # Empty request
            {
                "character_class": "wizard"
            },  # Missing level and spellcasting_ability_score
            {"level": 5},  # Missing character_class and spellcasting_ability_score
            {"spellcasting_ability_score": 16},  # Missing character_class and level
        ]

        for invalid_request in invalid_requests:
            response = client.post(
                "/game/spells/attack-bonus", json=invalid_request
            )
            assert response.status_code == 422, (
                f"Should reject invalid request: {invalid_request}"
            )

    def test_spell_attack_bonus_ability_modifier_calculation(self) -> None:
        """Test ability modifier calculation edge cases."""
        from app.main import app

        client = TestClient(app)

        # Test various ability scores
        test_cases = [
            (8, -1),  # 8 score = -1 modifier
            (10, 0),  # 10 score = 0 modifier
            (11, 0),  # 11 score = 0 modifier
            (12, 1),  # 12 score = +1 modifier
            (13, 1),  # 13 score = +1 modifier
            (18, 4),  # 18 score = +4 modifier
        ]

        for ability_score, expected_modifier in test_cases:
            request_data = {
                "character_class": "wizard",
                "level": 1,
                "spellcasting_ability_score": ability_score,
            }

            response = client.post("/game/spells/attack-bonus", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["ability_modifier"] == expected_modifier, (
                f"Score {ability_score} should give modifier {expected_modifier}, "
                f"got {data['ability_modifier']}"
            )

    def test_spell_attack_bonus_proficiency_levels(self) -> None:
        """Test proficiency bonus at different levels."""
        from app.main import app

        client = TestClient(app)

        # Test proficiency bonus progression
        test_cases = [
            (1, 2),  # Levels 1-4: +2
            (4, 2),  # Levels 1-4: +2
            (5, 3),  # Levels 5-8: +3
            (8, 3),  # Levels 5-8: +3
            (9, 4),  # Levels 9-12: +4
            (12, 4),  # Levels 9-12: +4
            (13, 5),  # Levels 13-16: +5
            (16, 5),  # Levels 13-16: +5
            (17, 6),  # Levels 17-20: +6
            (20, 6),  # Levels 17-20: +6
        ]

        for level, expected_proficiency in test_cases:
            request_data = {
                "character_class": "wizard",
                "level": level,
                "spellcasting_ability_score": 10,  # 0 modifier for easier testing
            }

            response = client.post("/game/spells/attack-bonus", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["proficiency_bonus"] == expected_proficiency, (
                f"Level {level} should give proficiency {expected_proficiency}, "
                f"got {data['proficiency_bonus']}"
            )

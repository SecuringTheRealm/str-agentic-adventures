"""
Tests for the NPC system API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestNPCSystemEndpoints:
    """Test suite for NPC system API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_create_campaign_npc(self, client):
        """Test creating a campaign NPC."""
        campaign_id = "test_campaign_123"
        request_data = {
            "campaign_id": campaign_id,
            "name": "Barthen the Merchant",
            "race": "Human",
            "gender": "Male",
            "age": 45,
            "occupation": "Merchant",
            "location": "Phandalin",
            "importance": "major",
            "story_role": "quest_giver"
        }
        
        response = client.post(f"/api/game/campaign/{campaign_id}/npcs", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Barthen the Merchant"
        assert data["race"] == "Human"
        assert data["gender"] == "Male"
        assert data["age"] == 45
        assert data["occupation"] == "Merchant"
        assert data["location"] == "Phandalin"
        assert data["campaign_id"] == campaign_id
        assert data["importance"] == "major"
        assert data["story_role"] == "quest_giver"
        
        # Check that personality was generated
        assert "personality" in data
        assert len(data["personality"]["traits"]) > 0
        assert len(data["personality"]["mannerisms"]) > 0
        
        # Check that abilities were generated
        assert "abilities" in data
        assert "hit_points" in data
        assert "armor_class" in data

    def test_create_npc_minimal_data(self, client):
        """Test creating NPC with minimal required data."""
        campaign_id = "test_campaign_123"
        request_data = {
            "campaign_id": campaign_id,
            "name": "Simple Guard"
        }
        
        response = client.post(f"/api/game/campaign/{campaign_id}/npcs", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Simple Guard"
        assert data["campaign_id"] == campaign_id
        assert data["importance"] == "minor"  # Default value
        assert "id" in data
        assert "personality" in data

    def test_get_npc_personality(self, client):
        """Test getting NPC personality."""
        npc_id = "test_npc_123"
        
        response = client.get(f"/api/game/npc/{npc_id}/personality")
        assert response.status_code == 200
        
        data = response.json()
        assert "traits" in data
        assert "ideals" in data
        assert "bonds" in data
        assert "flaws" in data
        assert "mannerisms" in data
        assert "appearance" in data
        assert "motivations" in data
        
        # Check that personality has meaningful content
        assert len(data["traits"]) > 0
        assert len(data["ideals"]) > 0
        assert isinstance(data["traits"], list)
        assert isinstance(data["ideals"], list)

    def test_log_npc_interaction(self, client):
        """Test logging NPC interaction."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "character_id": "char_456",
            "interaction_type": "conversation",
            "summary": "Discussed the missing supplies from the merchant caravan",
            "outcome": "NPC agreed to help investigate",
            "relationship_change": 10
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/interaction", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "interaction_id" in data
        assert data["interaction_id"] != ""
        assert "new_relationship_level" in data
        assert isinstance(data["new_relationship_level"], int)
        assert -100 <= data["new_relationship_level"] <= 100

    def test_log_npc_interaction_party(self, client):
        """Test logging NPC interaction with entire party."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "interaction_type": "trade",
            "summary": "Party purchased supplies for their journey",
            "outcome": "Successful trade",
            "relationship_change": 5
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/interaction", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "interaction_id" in data

    def test_generate_npc_stats_civilian(self, client):
        """Test generating civilian NPC stats."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "level": 1,
            "role": "civilian"
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/generate-stats", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "generated_stats" in data
        
        stats = data["generated_stats"]
        assert stats["level"] == 1
        assert stats["role"] == "civilian"
        assert "hit_points" in stats
        assert "armor_class" in stats
        assert "abilities" in stats
        assert "proficiency_bonus" in stats
        
        # Check hit points structure
        assert "current" in stats["hit_points"]
        assert "maximum" in stats["hit_points"]
        assert stats["hit_points"]["current"] > 0
        
        # Check abilities
        abilities = stats["abilities"]
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            assert ability in abilities
            assert isinstance(abilities[ability], int)
            assert 6 <= abilities[ability] <= 20  # Reasonable ability score range

    def test_generate_npc_stats_guard(self, client):
        """Test generating guard NPC stats."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "level": 2,
            "role": "guard"
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/generate-stats", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        stats = data["generated_stats"]
        
        assert stats["level"] == 2
        assert stats["role"] == "guard"
        assert stats["armor_class"] >= 14  # Guards should have better AC than civilians
        assert stats["hit_points"]["maximum"] > 4  # Guards should have more HP

    def test_generate_npc_stats_spellcaster(self, client):
        """Test generating spellcaster NPC stats."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "level": 3,
            "role": "spellcaster"
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/generate-stats", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        stats = data["generated_stats"]
        
        assert stats["level"] == 3
        assert stats["role"] == "spellcaster"
        # Spellcasters should have higher mental stats
        abilities = stats["abilities"]
        assert abilities["intelligence"] >= 12 or abilities["wisdom"] >= 12

    def test_generate_npc_stats_default_level(self, client):
        """Test generating NPC stats with default level."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "role": "soldier"
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/generate-stats", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        stats = data["generated_stats"]
        
        assert stats["level"] == 1  # Default level
        assert stats["role"] == "soldier"

    def test_generate_npc_stats_high_level(self, client):
        """Test generating high-level NPC stats."""
        npc_id = "test_npc_123"
        request_data = {
            "npc_id": npc_id,
            "level": 10,
            "role": "soldier"
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/generate-stats", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        stats = data["generated_stats"]
        
        assert stats["level"] == 10
        assert stats["proficiency_bonus"] >= 4  # High level = higher proficiency
        assert stats["hit_points"]["maximum"] >= 20  # Should have more HP at high level

    def test_npc_personality_structure(self, client):
        """Test that NPC personality has proper structure."""
        npc_id = "test_npc_123"
        
        response = client.get(f"/api/game/npc/{npc_id}/personality")
        assert response.status_code == 200
        
        data = response.json()
        
        # All personality fields should be present
        required_fields = ["traits", "ideals", "bonds", "flaws", "mannerisms", "motivations"]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], list)
        
        # Optional fields
        optional_fields = ["appearance"]
        for field in optional_fields:
            if field in data:
                assert isinstance(data[field], (str, type(None)))

    def test_interaction_relationship_bounds(self, client):
        """Test that relationship levels stay within bounds."""
        npc_id = "test_npc_123"
        
        # Test extreme positive change
        request_data = {
            "npc_id": npc_id,
            "interaction_type": "heroic_deed",
            "summary": "Saved the NPC's life",
            "relationship_change": 200  # Extreme value
        }
        
        response = client.post(f"/api/game/npc/{npc_id}/interaction", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert -100 <= data["new_relationship_level"] <= 100  # Should be clamped

    def test_npc_creation_personality_generation(self, client):
        """Test that created NPCs have diverse personalities."""
        campaign_id = "test_campaign_123"
        
        # Create multiple NPCs and check personality diversity
        npcs = []
        for i in range(3):
            request_data = {
                "campaign_id": campaign_id,
                "name": f"Test NPC {i}"
            }
            
            response = client.post(f"/api/game/campaign/{campaign_id}/npcs", json=request_data)
            assert response.status_code == 200
            npcs.append(response.json())
        
        # Check that personalities are different (at least some variation)
        trait_sets = [set(npc["personality"]["traits"]) for npc in npcs]
        
        # At least some NPCs should have different traits
        unique_traits = set()
        for trait_set in trait_sets:
            unique_traits.update(trait_set)
        
        assert len(unique_traits) > 2  # Should have some variety in traits
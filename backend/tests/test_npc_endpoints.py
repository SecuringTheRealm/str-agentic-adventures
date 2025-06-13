"""
Test NPC management endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.dungeon_master_agent import DungeonMasterAgent
from app.models.game_models import CreateNPCRequest, UpdateNPCRequest, NPCPersonality


class TestNPCEndpoints:
    """Test NPC management functionality."""

    @pytest.fixture
    def dm_agent(self):
        """Create a DungeonMasterAgent instance for testing."""
        with patch('app.agents.dungeon_master_agent.kernel_manager'):
            agent = DungeonMasterAgent()
            # Set up a test campaign
            agent.active_sessions = {
                "test_campaign": {
                    "id": "test_campaign",
                    "name": "Test Campaign",
                    "npcs": {}
                }
            }
            return agent

    @pytest.mark.asyncio
    async def test_create_npc_basic(self, dm_agent):
        """Test creating a basic NPC."""
        npc_data = {
            "name": "Test NPC",
            "description": "A test character",
            "role": "ally"
        }
        
        result = await dm_agent.create_campaign_npc("test_campaign", npc_data)
        
        assert "error" not in result
        assert result["name"] == "Test NPC"
        assert result["role"] == "ally"
        assert result["status"] == "alive"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_create_npc_with_stats(self, dm_agent):
        """Test creating an NPC with generated stats."""
        npc_data = {
            "name": "Warrior NPC",
            "description": "A warrior character", 
            "role": "antagonist",
            "generate_stats": True
        }
        
        result = await dm_agent.create_campaign_npc("test_campaign", npc_data)
        
        assert "error" not in result
        assert result["name"] == "Warrior NPC"
        assert result["stats"] is not None
        assert result["stats"]["level"] == 5  # Antagonist gets level 5
        assert result["stats"]["armor_class"] == 16

    @pytest.mark.asyncio
    async def test_get_campaign_npcs(self, dm_agent):
        """Test getting all NPCs for a campaign."""
        # First create an NPC
        npc_data = {
            "name": "Test NPC",
            "description": "A test character",
            "role": "neutral"
        }
        await dm_agent.create_campaign_npc("test_campaign", npc_data)
        
        # Get NPCs
        result = await dm_agent.get_campaign_npcs("test_campaign")
        
        assert "error" not in result
        assert "npcs" in result
        assert len(result["npcs"]) == 1

    @pytest.mark.asyncio
    async def test_update_npc(self, dm_agent):
        """Test updating an existing NPC."""
        # First create an NPC
        npc_data = {
            "name": "Test NPC",
            "description": "A test character",
            "role": "neutral"
        }
        created_npc = await dm_agent.create_campaign_npc("test_campaign", npc_data)
        npc_id = created_npc["id"]
        
        # Update the NPC
        update_data = {
            "description": "Updated description",
            "role": "ally"
        }
        result = await dm_agent.update_campaign_npc("test_campaign", npc_id, update_data)
        
        assert "error" not in result
        assert result["description"] == "Updated description"
        assert result["role"] == "ally"
        assert result["name"] == "Test NPC"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_npc(self, dm_agent):
        """Test deleting an NPC."""
        # First create an NPC
        npc_data = {
            "name": "Test NPC",
            "description": "A test character",
            "role": "neutral"
        }
        created_npc = await dm_agent.create_campaign_npc("test_campaign", npc_data)
        npc_id = created_npc["id"]
        
        # Delete the NPC
        result = await dm_agent.delete_campaign_npc("test_campaign", npc_id)
        
        assert "error" not in result
        assert result["success"] is True
        
        # Verify it's gone
        npcs_result = await dm_agent.get_campaign_npcs("test_campaign")
        assert len(npcs_result["npcs"]) == 0

    @pytest.mark.asyncio
    async def test_create_npc_invalid_campaign(self, dm_agent):
        """Test creating an NPC for a non-existent campaign."""
        npc_data = {
            "name": "Test NPC",
            "description": "A test character",
            "role": "neutral"
        }
        
        result = await dm_agent.create_campaign_npc("invalid_campaign", npc_data)
        
        assert "error" in result
        assert result["error"] == "Campaign not found"

    @pytest.mark.asyncio
    async def test_update_npc_not_found(self, dm_agent):
        """Test updating a non-existent NPC."""
        update_data = {
            "description": "Updated description"
        }
        
        result = await dm_agent.update_campaign_npc("test_campaign", "invalid_npc", update_data)
        
        assert "error" in result
        assert result["error"] == "NPC not found"

    @pytest.mark.asyncio
    async def test_delete_npc_not_found(self, dm_agent):
        """Test deleting a non-existent NPC."""
        result = await dm_agent.delete_campaign_npc("test_campaign", "invalid_npc")
        
        assert "error" in result
        assert result["error"] == "NPC not found"
"""
Tests for the narrative generation system.
"""

import pytest
from unittest.mock import patch
from app.plugins.narrative_generation_plugin import NarrativeGenerationPlugin
from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
from app.agents.narrator_agent import NarratorAgent
from app.models.game_models import NarrativeState


class TestNarrativeGenerationPlugin:
    """Test cases for the narrative generation plugin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = NarrativeGenerationPlugin()

    def test_create_story_arc(self):
        """Test story arc creation."""
        result = self.plugin.create_story_arc(
            title="Test Adventure",
            description="A test adventure for heroes",
            arc_type="main",
            themes="adventure, heroism",
            character_ids="char1, char2",
        )

        assert result["status"] == "success"
        assert result["story_arc_id"] in self.plugin.story_arcs
        assert result["plot_points_generated"] > 0

        # Verify story arc details
        story_arc = self.plugin.story_arcs[result["story_arc_id"]]
        assert story_arc.title == "Test Adventure"
        assert story_arc.type == "main"
        assert "adventure" in story_arc.themes
        assert "char1" in story_arc.characters_involved
        assert len(story_arc.plot_points) > 0

    def test_generate_choices(self):
        """Test narrative choice generation."""
        result = self.plugin.generate_choices(
            situation="You encounter a locked door",
            choice_type="exploration",
            num_choices=3,
        )

        assert result["status"] == "success"
        assert len(result["choices"]) == 3

        # Verify choices have required fields
        for choice in result["choices"]:
            assert "id" in choice
            assert "text" in choice
            assert "description" in choice
            assert choice["id"] in self.plugin.narrative_choices

    def test_process_choice(self):
        """Test choice processing and consequence application."""
        # First generate a choice
        choice_result = self.plugin.generate_choices(
            situation="Test situation", choice_type="social", num_choices=1
        )

        choice_id = choice_result["choices"][0]["id"]
        campaign_id = "test_campaign"

        # Process the choice
        process_result = self.plugin.process_choice(
            choice_id=choice_id, campaign_id=campaign_id, character_id="test_character"
        )

        assert process_result["status"] == "success"
        assert "consequences" in process_result
        assert campaign_id in self.plugin.narrative_states

        # Verify event was recorded
        assert len(self.plugin.narrative_events) > 0
        event = self.plugin.narrative_events[-1]
        assert event.event_type == "choice_made"
        assert choice_id in event.choices_made

    def test_advance_narrative(self):
        """Test narrative advancement and plot point triggers."""
        campaign_id = "test_campaign"

        # Create a story arc first
        arc_result = self.plugin.create_story_arc(
            title="Test Arc", description="Test", arc_type="main"
        )

        # Initialize narrative state with the arc
        narrative_state = NarrativeState(campaign_id=campaign_id)
        narrative_state.active_story_arcs = [arc_result["story_arc_id"]]
        self.plugin.narrative_states[campaign_id] = narrative_state

        # Advance narrative
        advance_result = self.plugin.advance_narrative(
            campaign_id=campaign_id,
            current_situation="The adventure begins",
            trigger_data='{"story_progress": 0.1}',
        )

        assert advance_result["status"] == "success"
        assert "new_choices" in advance_result

        # Verify narrative state was updated
        updated_state = self.plugin.narrative_states[campaign_id]
        assert len(updated_state.pending_choices) > 0

    def test_get_narrative_state(self):
        """Test retrieving narrative state."""
        campaign_id = "test_campaign"

        # Create initial state
        narrative_state = NarrativeState(campaign_id=campaign_id)
        self.plugin.narrative_states[campaign_id] = narrative_state

        # Get state
        result = self.plugin.get_narrative_state(campaign_id)

        assert result["status"] == "success"
        assert result["campaign_id"] == campaign_id
        assert "active_story_arcs" in result
        assert "pending_choices" in result


class TestNarrativeMemoryPlugin:
    """Test cases for the enhanced narrative memory plugin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = NarrativeMemoryPlugin()

    def test_track_story_arc(self):
        """Test story arc tracking functionality."""
        result = self.plugin.track_story_arc(
            arc_id="arc_1",
            arc_title="Test Arc",
            progress="Beginning of the adventure",
            key_events="Met the mentor, Found the map",
            character_impact="Characters are motivated",
        )

        assert result["status"] == "success"
        assert "arc_1" in self.plugin.story_arcs

        # Verify arc details
        arc_memory = self.plugin.story_arcs["arc_1"]
        assert arc_memory["title"] == "Test Arc"
        assert arc_memory["progress"] == "Beginning of the adventure"
        assert "Met the mentor" in arc_memory["key_events"]
        assert arc_memory["character_impact"] == "Characters are motivated"

    def test_record_character_development(self):
        """Test character development recording."""
        result = self.plugin.record_character_development(
            character_id="char_1",
            development_type="personality",
            description="Showed courage in the face of danger",
            story_arc_id="arc_1",
        )

        assert result["status"] == "success"
        assert "char_1" in self.plugin.character_arcs

        # Verify development entry
        developments = self.plugin.character_arcs["char_1"]
        assert len(developments) == 1
        assert developments[0]["type"] == "personality"
        assert developments[0]["description"] == "Showed courage in the face of danger"

    def test_recall_story_arcs(self):
        """Test story arc recall functionality."""
        # Add some test data
        self.plugin.track_story_arc(
            arc_id="arc_1", arc_title="Test Arc 1", progress="active"
        )

        self.plugin.track_story_arc(
            arc_id="arc_2", arc_title="Test Arc 2", progress="completed"
        )

        # Recall all arcs
        result = self.plugin.recall_story_arcs()

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["story_arcs"]) == 2

        # Test filtering by status
        active_result = self.plugin.recall_story_arcs(status="active")
        assert active_result["status"] == "success"
        assert active_result["count"] == 1


class TestNarratorAgent:
    """Test cases for the enhanced narrator agent."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures."""
        with patch("app.agents.narrator_agent.kernel_manager"):
            self.narrator = NarratorAgent()

    @pytest.mark.asyncio
    async def test_describe_scene_with_narrative_context(self):
        """Test scene description with narrative context."""
        scene_context = {
            "location": "Ancient Temple",
            "time": "midnight",
            "mood": "mysterious",
            "campaign_id": "test_campaign",
            "characters": "Elara, Thorne",
        }

        description = await self.narrator.describe_scene(scene_context)

        assert "Ancient Temple" in description
        assert "midnight" in description
        assert len(description) > 50  # Should be a rich description

    @pytest.mark.asyncio
    async def test_process_action_with_choices(self):
        """Test action processing with narrative choice generation."""
        action = "investigate the mysterious altar"
        context = {
            "campaign_id": "test_campaign",
            "character_id": "char_1",
            "location": "Temple",
        }

        result = await self.narrator.process_action(action, context)

        assert result["success"] is True
        assert "investigate" in result["description"].lower()
        assert "state_updates" in result

    @pytest.mark.asyncio
    async def test_create_campaign_story(self):
        """Test campaign story creation."""
        campaign_context = {
            "campaign_id": "new_campaign",
            "setting": "fantasy",
            "tone": "heroic",
            "characters": ["Hero1", "Hero2"],
            "name": "The Great Adventure",
        }

        result = await self.narrator.create_campaign_story(campaign_context)

        assert result["success"] is True
        assert "created_arcs" in result
        assert result["campaign_id"] == "new_campaign"

    @pytest.mark.asyncio
    async def test_get_narrative_status(self):
        """Test narrative status retrieval."""
        campaign_id = "test_campaign"

        # First create a campaign story
        campaign_context = {
            "campaign_id": campaign_id,
            "setting": "fantasy",
            "tone": "heroic",
            "characters": ["Hero1"],
        }

        await self.narrator.create_campaign_story(campaign_context)

        # Then get status
        status = await self.narrator.get_narrative_status(campaign_id)

        assert "narrative_state" in status or "message" in status
        # Note: Due to mocking, some features might not work perfectly in tests


class TestNarrativeIntegration:
    """Integration tests for the complete narrative system."""

    def test_narrative_flow_integration(self):
        """Test complete narrative flow from arc creation to choice processing."""
        # Create plugins
        narrative_gen = NarrativeGenerationPlugin()
        narrative_memory = NarrativeMemoryPlugin()

        campaign_id = "integration_test"

        # 1. Create story arc
        arc_result = narrative_gen.create_story_arc(
            title="Integration Test Adventure",
            description="A test of the complete narrative system",
            arc_type="main",
            themes="testing, integration",
            character_ids="test_hero",
        )

        assert arc_result["status"] == "success"
        arc_id = arc_result["story_arc_id"]

        # 2. Track in memory
        memory_result = narrative_memory.track_story_arc(
            arc_id=arc_id,
            arc_title="Integration Test Adventure",
            progress="Just started",
            key_events="Arc created",
            character_impact="Hero is ready for adventure",
        )

        assert memory_result["status"] == "success"

        # 3. Generate choices
        choices_result = narrative_gen.generate_choices(
            situation="The adventure begins at a crossroads",
            choice_type="exploration",
            num_choices=2,
        )

        assert choices_result["status"] == "success"
        assert len(choices_result["choices"]) == 2

        # 4. Process a choice
        choice_id = choices_result["choices"][0]["id"]
        process_result = narrative_gen.process_choice(
            choice_id=choice_id, campaign_id=campaign_id, character_id="test_hero"
        )

        assert process_result["status"] == "success"

        # 5. Advance narrative
        advance_result = narrative_gen.advance_narrative(
            campaign_id=campaign_id,
            current_situation="After making the first choice",
            trigger_data='{"choice_made": true}',
        )

        assert advance_result["status"] == "success"

        # 6. Verify final state
        final_state = narrative_gen.get_narrative_state(campaign_id)
        assert final_state["status"] == "success"

        # 7. Check memory integration
        arc_recall = narrative_memory.recall_story_arcs()
        assert arc_recall["status"] == "success"
        assert len(arc_recall["story_arcs"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__])

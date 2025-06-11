"""
Integration example showing how the narrative generation system 
integrates with the existing game API and agent architecture.
"""
from typing import Dict, Any
from app.plugins.narrative_generation_plugin import NarrativeGenerationPlugin
from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
from app.models.game_models import (
    Campaign, CreateCampaignRequest, PlayerInput, GameResponse, 
    NarrativeState
)


class EnhancedGameService:
    """
    Enhanced game service that integrates narrative generation with existing functionality.
    This demonstrates how the new narrative system fits into the existing architecture.
    """
    
    def __init__(self):
        self.narrative_gen = NarrativeGenerationPlugin()
        self.narrative_memory = NarrativeMemoryPlugin()
        self.campaigns = {}  # Campaign storage
        
    def create_campaign(self, request: CreateCampaignRequest) -> Dict[str, Any]:
        """
        Create a new campaign with integrated narrative generation.
        """
        try:
            # Create basic campaign
            campaign = Campaign(
                name=request.name,
                setting=request.setting,
                tone=request.tone or "heroic",
                homebrew_rules=request.homebrew_rules or []
            )
            
            # Store campaign
            self.campaigns[campaign.id] = campaign
            
            # Create main story arc using narrative generation
            main_arc_result = self.narrative_gen.create_story_arc(
                title=f"The {request.setting.title()} Chronicles",
                description=f"An epic {request.tone or 'heroic'} adventure in {request.setting}",
                arc_type="main",
                themes=f"{request.tone or 'heroic'}, adventure, {request.setting}",
                character_ids=""  # Will be updated when characters join
            )
            
            if main_arc_result["status"] == "success":
                # Initialize narrative state
                narrative_state = NarrativeState(campaign_id=campaign.id)
                narrative_state.active_story_arcs = [main_arc_result["story_arc_id"]]
                self.narrative_gen.narrative_states[campaign.id] = narrative_state
                
                # Track in memory
                self.narrative_memory.track_story_arc(
                    arc_id=main_arc_result["story_arc_id"],
                    arc_title=f"The {request.setting.title()} Chronicles",
                    progress="Campaign created, awaiting adventurers",
                    key_events="Campaign established",
                    character_impact="Setting prepared for heroes"
                )
                
                # Record campaign creation
                self.narrative_memory.record_event(
                    f"Campaign '{request.name}' created",
                    request.setting,
                    "",
                    8
                )
            
            return {
                "success": True,
                "campaign": campaign.model_dump(),
                "narrative_arc": main_arc_result,
                "message": f"Campaign '{request.name}' created with narrative structure"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create campaign: {str(e)}"
            }
    
    def process_player_input(self, player_input: PlayerInput) -> GameResponse:
        """
        Process player input with enhanced narrative generation.
        """
        try:
            message = player_input.message
            campaign_id = player_input.campaign_id
            character_id = player_input.character_id
            
            # Get current narrative state
            narrative_state = self.narrative_gen.get_narrative_state(campaign_id)
            
            # Determine action type for choice generation
            choice_type = "general"
            if any(word in message.lower() for word in ["fight", "attack", "combat"]):
                choice_type = "combat"
            elif any(word in message.lower() for word in ["talk", "speak", "persuade"]):
                choice_type = "social"
            elif any(word in message.lower() for word in ["explore", "investigate", "search"]):
                choice_type = "exploration"
            
            # Generate narrative choices
            choices_result = self.narrative_gen.generate_choices(
                situation=message,
                choice_type=choice_type,
                num_choices=3
            )
            
            # Advance narrative
            advance_result = self.narrative_gen.advance_narrative(
                campaign_id=campaign_id,
                current_situation=message,
                trigger_data=f'{{"action": "{message}", "character_id": "{character_id}"}}'
            )
            
            # Build response
            response_message = f"In response to your action '{message}'..."
            
            # Add narrative context
            if advance_result.get("activated_plot_points"):
                response_message += " Your actions have triggered significant story developments!"
                
            if advance_result.get("completed_plot_points"):
                response_message += " You have successfully resolved important story elements!"
            
            # Prepare state updates
            state_updates = {
                "narrative_choices": choices_result.get("choices", []),
                "plot_points_activated": advance_result.get("activated_plot_points", []),
                "narrative_state": narrative_state
            }
            
            # Record action in memory
            self.narrative_memory.record_event(
                f"Player action: {message}",
                "current location",  # Would be retrieved from game state
                character_id,
                5
            )
            
            return GameResponse(
                message=response_message,
                state_updates=state_updates
            )
            
        except Exception as e:
            return GameResponse(
                message=f"An error occurred processing your action: {str(e)}",
                state_updates={}
            )
    
    def get_campaign_narrative_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive narrative status for a campaign.
        """
        try:
            # Get narrative state
            narrative_state = self.narrative_gen.get_narrative_state(campaign_id)
            
            # Get story arc summaries
            story_arcs = self.narrative_memory.recall_story_arcs()
            
            # Get recent events
            recent_events = self.narrative_memory.recall_timeline(limit=10)
            
            # Get campaign info
            campaign = self.campaigns.get(campaign_id)
            
            return {
                "success": True,
                "campaign": campaign.model_dump() if campaign else None,
                "narrative_state": narrative_state,
                "story_arcs": story_arcs,
                "recent_events": recent_events,
                "summary": {
                    "active_arcs": len(narrative_state.get("active_story_arcs", [])) if narrative_state.get("status") == "success" else 0,
                    "pending_choices": len(narrative_state.get("pending_choices", [])) if narrative_state.get("status") == "success" else 0,
                    "total_events": len(self.narrative_memory.events)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get narrative status: {str(e)}"
            }
    
    def make_narrative_choice(self, campaign_id: str, character_id: str, choice_id: str) -> Dict[str, Any]:
        """
        Process a player's narrative choice selection.
        """
        try:
            # Process the choice
            process_result = self.narrative_gen.process_choice(
                choice_id=choice_id,
                campaign_id=campaign_id,
                character_id=character_id
            )
            
            if process_result["status"] == "success":
                # Record character development based on choice
                choice = self.narrative_gen.narrative_choices.get(choice_id)
                if choice:
                    self.narrative_memory.record_character_development(
                        character_id=character_id,
                        development_type="decision_making",
                        description=f"Made choice: {choice.text}",
                        story_arc_id=""
                    )
                
                # Advance narrative after choice
                advance_result = self.narrative_gen.advance_narrative(
                    campaign_id=campaign_id,
                    current_situation=f"After choosing: {choice.text if choice else 'unknown choice'}",
                    trigger_data=f'{{"choice_made": "{choice_id}", "character_id": "{character_id}"}}'
                )
                
                return {
                    "success": True,
                    "choice_result": process_result,
                    "narrative_advancement": advance_result,
                    "message": "Choice processed and narrative advanced"
                }
            else:
                return process_result
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to process choice: {str(e)}"
            }


def demonstrate_api_integration():
    """
    Demonstrate the enhanced game service with narrative integration.
    """
    print("=== Enhanced Game Service Demo ===\n")
    
    # Initialize service
    service = EnhancedGameService()
    
    # 1. Create a campaign
    print("🎮 Creating a new campaign...")
    campaign_request = CreateCampaignRequest(
        name="The Dragon's Bane",
        setting="fantasy realm of Astoria",
        tone="heroic",
        homebrew_rules=["Critical hits deal maximum damage", "Magic is rare and powerful"]
    )
    
    campaign_result = service.create_campaign(campaign_request)
    print(f"✅ {campaign_result['message']}")
    
    if campaign_result["success"]:
        campaign_id = campaign_result["campaign"]["id"]
        
        # 2. Simulate player input
        print("\n🎭 Processing player input...")
        player_input = PlayerInput(
            message="I want to investigate the mysterious tower on the horizon",
            character_id="hero_knight_001",
            campaign_id=campaign_id
        )
        
        response = service.process_player_input(player_input)
        print(f"🎪 Game Response: {response.message}")
        
        # Show available choices
        if "narrative_choices" in response.state_updates:
            choices = response.state_updates["narrative_choices"]
            print(f"\n📝 Available narrative choices ({len(choices)}):")
            for i, choice in enumerate(choices, 1):
                print(f"   {i}. {choice['text']}")
        
        # 3. Make a narrative choice
        if choices:
            print(f"\n⚡ Making choice: {choices[0]['text']}")
            choice_result = service.make_narrative_choice(
                campaign_id=campaign_id,
                character_id="hero_knight_001",
                choice_id=choices[0]["id"]
            )
            print(f"✅ {choice_result['message']}")
        
        # 4. Get narrative status
        print("\n📊 Campaign Narrative Status:")
        status = service.get_campaign_narrative_status(campaign_id)
        
        if status["success"]:
            summary = status["summary"]
            print(f"   - Active story arcs: {summary['active_arcs']}")
            print(f"   - Pending choices: {summary['pending_choices']}")
            print(f"   - Total events: {summary['total_events']}")
            
            # Show recent events
            if status["recent_events"]["status"] == "success":
                print("   - Recent events:")
                for event in status["recent_events"]["events"][:3]:
                    print(f"     • {event['description']}")
    
    print("\n🎉 API Integration demonstration complete!")
    print("\nThe enhanced system provides:")
    print("✓ Seamless integration with existing Campaign and PlayerInput models")
    print("✓ Enhanced GameResponse with narrative choices and story updates")
    print("✓ Comprehensive narrative status tracking")
    print("✓ Automatic story arc creation for new campaigns")
    print("✓ Character development tracking through choices")


if __name__ == "__main__":
    demonstrate_api_integration()
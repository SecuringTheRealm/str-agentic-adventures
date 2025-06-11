"""
Example usage of the narrative generation system.
This demonstrates how to create dynamic storylines, branching narratives,
and integrate with AI agent functionality.
"""
import asyncio
from app.plugins.narrative_generation_plugin import NarrativeGenerationPlugin
from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin


async def demonstrate_narrative_system():
    """
    Demonstrate the complete narrative generation system workflow.
    """
    print("=== AI Dungeon Master Narrative Generation System Demo ===\n")
    
    # Initialize components
    narrative_gen = NarrativeGenerationPlugin()
    narrative_memory = NarrativeMemoryPlugin()
    
    print("🎭 Creating a new campaign story...")
    
    # 1. Create a main story arc
    main_arc_result = narrative_gen.create_story_arc(
        title="The Lost Crown of Eldoria",
        description="An epic quest to recover the ancient crown and restore peace to the realm",
        arc_type="main",
        themes="heroism, adventure, ancient magic, political intrigue",
        character_ids="hero_warrior, hero_mage, hero_rogue"
    )
    
    print(f"✅ Main story arc created: {main_arc_result['message']}")
    print(f"   - Plot points generated: {main_arc_result['plot_points_generated']}")
    
    # Track the arc in memory
    narrative_memory.track_story_arc(
        arc_id=main_arc_result["story_arc_id"],
        arc_title="The Lost Crown of Eldoria",
        progress="The heroes have been called to action",
        key_events="Received quest from the dying king",
        character_impact="Party is united in purpose"
    )
    
    # 2. Create a character development arc
    character_arc_result = narrative_gen.create_story_arc(
        title="Bonds of Trust",
        description="The party learns to work together despite their differences",
        arc_type="character",
        themes="friendship, trust, teamwork",
        character_ids="hero_warrior, hero_mage, hero_rogue"
    )
    
    print(f"✅ Character arc created: {character_arc_result['message']}")
    
    # 3. Simulate the first major decision point
    print("\n🎯 First Major Decision Point:")
    print("The party arrives at a crossroads. An ancient map shows three possible paths to the crown:")
    
    choices_result = narrative_gen.generate_choices(
        situation="Standing at the crossroads with three paths: the Mountain Pass (dangerous but direct), the Enchanted Forest (magical but unpredictable), and the Coastal Route (longer but safer)",
        choice_type="exploration",
        num_choices=3
    )
    
    print("\n📝 Available Choices:")
    for i, choice in enumerate(choices_result["choices"], 1):
        print(f"   {i}. {choice['text']}")
        print(f"      {choice['description']}")
    
    # 4. Process the party's choice (simulate choosing option 1)
    chosen_choice = choices_result["choices"][0]
    print(f"\n⚡ Party chooses: {chosen_choice['text']}")
    
    process_result = narrative_gen.process_choice(
        choice_id=chosen_choice["id"],
        campaign_id="demo_campaign",
        character_id="hero_warrior"
    )
    
    print(f"✅ Choice processed: {process_result['message']}")
    print(f"   - Consequences: {process_result['consequences']}")
    
    # Record character development
    narrative_memory.record_character_development(
        character_id="hero_warrior",
        development_type="leadership",
        description="Took initiative in making difficult decision at the crossroads",
        story_arc_id=character_arc_result["story_arc_id"]
    )
    
    # 5. Advance the narrative
    print("\n🔄 Advancing the narrative...")
    
    advance_result = narrative_gen.advance_narrative(
        campaign_id="demo_campaign",
        current_situation="The party has committed to investigating further and discovers ancient ruins",
        trigger_data='{"exploration_begun": true, "ancient_site_discovered": true}'
    )
    
    if advance_result["activated_plot_points"]:
        print("📈 Plot points activated:")
        for point in advance_result["activated_plot_points"]:
            print(f"   - {point['title']} ({point['type']})")
    
    if advance_result["new_choices"]:
        print("\n🆕 New choices emerged:")
        for choice in advance_result["new_choices"]:
            print(f"   - {choice['text']}")
    
    # 6. Show narrative state
    print("\n📊 Current Narrative State:")
    narrative_state = narrative_gen.get_narrative_state("demo_campaign")
    
    if narrative_state["status"] == "success":
        print(f"   - Active story arcs: {len(narrative_state['active_story_arcs'])}")
        print(f"   - Pending choices: {len(narrative_state['pending_choices'])}")
        print(f"   - Last updated: {narrative_state['last_updated']}")
    
    # 7. Show memory integration
    print("\n🧠 Story Memory Integration:")
    
    # Recent events
    timeline = narrative_memory.recall_timeline(limit=3)
    if timeline["status"] == "success":
        print("   Recent events:")
        for event in timeline["events"]:
            print(f"   - {event['description']} ({event['timestamp'][:19]})")
    
    # Story arcs
    arcs = narrative_memory.recall_story_arcs()
    if arcs["status"] == "success":
        print(f"   Tracked story arcs: {arcs['count']}")
        for arc in arcs["story_arcs"]:
            print(f"   - {arc['title']}: {arc['progress']}")
    
    print("\n🎉 Narrative generation system demonstration complete!")
    print("\nThe system successfully created:")
    print("✓ Dynamic story arcs with automatic plot point generation")
    print("✓ Branching narrative choices with consequences")
    print("✓ Character development tracking")
    print("✓ Story progression and state management")
    print("✓ Memory integration for narrative continuity")


async def demonstrate_narrator_agent_integration():
    """
    Demonstrate how the narrator agent integrates with the narrative system.
    """
    print("\n=== Narrator Agent Integration Demo ===\n")
    
    try:
        # Note: This requires proper Semantic Kernel setup with API keys
        # For demo purposes, we'll show the interface
        print("🤖 Narrator Agent would integrate as follows:")
        print("\n1. Scene Description with Narrative Context:")
        print("   - Incorporates active story arcs")
        print("   - Uses memory for location history")
        print("   - Adjusts mood based on narrative state")
        
        print("\n2. Action Processing with Choice Generation:")
        print("   - Analyzes player actions for narrative impact")
        print("   - Generates contextual choices")
        print("   - Tracks character development")
        
        print("\n3. Campaign Story Creation:")
        print("   - Initializes story arcs for new campaigns")
        print("   - Sets up narrative structure")
        print("   - Creates initial plot points")
        
        print("\n📝 Example Scene Description:")
        scene_context = {
            "location": "Ancient Ruins of the Lost Kingdom",
            "time": "twilight",
            "mood": "mysterious",
            "campaign_id": "demo_campaign",
            "characters": "brave adventurers"
        }
        
        print(f"   Context: {scene_context}")
        print("   Generated Description:")
        print("   'You find yourself in Ancient Ruins of the Lost Kingdom during twilight.")
        print("    Mystery hangs in the air like a thick fog, hinting at secrets yet to be discovered.")
        print("    Your ongoing adventures in The Lost Crown of Eldoria weigh on your mind.'")
        
    except Exception as e:
        print(f"⚠️  Full narrator agent demo requires proper Semantic Kernel setup: {e}")


def demonstrate_branching_narratives():
    """
    Show how the system handles complex branching narratives.
    """
    print("\n=== Branching Narratives Demo ===\n")
    
    narrative_gen = NarrativeGenerationPlugin()
    
    print("🌿 Creating a complex branching scenario...")
    
    # Create multiple story paths
    scenarios = [
        {
            "situation": "You discover the crown is protected by an ancient guardian",
            "choice_type": "combat",
            "description": "Combat scenario - fight or find alternative"
        },
        {
            "situation": "A local lord offers to help in exchange for a favor",
            "choice_type": "social",
            "description": "Social scenario - negotiate or decline"
        },
        {
            "situation": "You find a hidden passage that might lead to the crown",
            "choice_type": "exploration", 
            "description": "Exploration scenario - investigate or continue main path"
        }
    ]
    
    print("🎭 Generated branching choices:")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['description']}")
        print(f"   Situation: {scenario['situation']}")
        
        choices = narrative_gen.generate_choices(
            situation=scenario["situation"],
            choice_type=scenario["choice_type"],
            num_choices=2
        )
        
        if choices["status"] == "success":
            for j, choice in enumerate(choices["choices"], 1):
                print(f"   Choice {j}: {choice['text']}")
    
    print("\n💡 Each choice leads to different narrative branches:")
    print("   - Combat choices affect party reputation and resources")
    print("   - Social choices influence relationships and alliances") 
    print("   - Exploration choices reveal lore and alternative paths")
    print("   - All choices contribute to character development arcs")


if __name__ == "__main__":
    async def main():
        await demonstrate_narrative_system()
        await demonstrate_narrator_agent_integration()
        demonstrate_branching_narratives()
    
    asyncio.run(main())
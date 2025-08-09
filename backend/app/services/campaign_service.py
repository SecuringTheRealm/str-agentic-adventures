"""Campaign service for managing campaign operations."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_

from app.database import get_session
from app.models.db_models import Campaign as CampaignDB
from app.models.game_models import Campaign, CreateCampaignRequest


def campaign_to_dict(campaign: Campaign) -> dict[str, Any]:
    """Convert Campaign object to JSON-serializable dict."""
    data = campaign.model_dump()
    # Convert datetime to ISO string
    if "created_at" in data and isinstance(data["created_at"], datetime):
        data["created_at"] = data["created_at"].isoformat()
    return data


def dict_to_campaign(data: dict[str, Any]) -> Campaign:
    """Convert dict back to Campaign object."""
    # Convert ISO string back to datetime if needed
    if "created_at" in data and isinstance(data["created_at"], str):
        try:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        except ValueError:
            data["created_at"] = datetime.now()
    return Campaign.model_validate(data)


class CampaignService:
    """Service for campaign management operations."""

    def __init__(self) -> None:
        """Initialize the campaign service."""
        pass

    def create_campaign(
        self, campaign_data: CreateCampaignRequest, is_custom: bool = True
    ) -> Campaign:
        """Create a new campaign and persist it to database."""
        campaign_id = str(uuid.uuid4())

        # Create campaign object
        campaign = Campaign(
            id=campaign_id,
            name=campaign_data.name,
            setting=campaign_data.setting,
            tone=campaign_data.tone or "heroic",
            homebrew_rules=campaign_data.homebrew_rules or [],
            description=campaign_data.description,
        )

        # Save to database
        with next(get_session()) as db:
            db_campaign = CampaignDB(
                id=campaign_id,
                name=campaign_data.name,
                description=campaign_data.description,
                setting=campaign_data.setting,
                tone=campaign_data.tone or "heroic",
                homebrew_rules=campaign_data.homebrew_rules or [],
                is_custom=is_custom,
                is_template=False,
                data=campaign_to_dict(campaign),
            )
            db.add(db_campaign)
            db.commit()
            db.refresh(db_campaign)

        return campaign

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        """Retrieve a campaign by ID."""
        with next(get_session()) as db:
            db_campaign = (
                db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
            )
            if db_campaign:
                return dict_to_campaign(db_campaign.data)
            return None

    def list_campaigns(
        self, include_templates: bool = True, include_custom: bool = True
    ) -> list[Campaign]:
        """List campaigns based on filters."""
        with next(get_session()) as db:
            query = db.query(CampaignDB)

            conditions = []
            if include_templates:
                conditions.append(CampaignDB.is_template)
            if include_custom:
                conditions.append(CampaignDB.is_custom)

            if conditions:
                query = query.filter(or_(*conditions))

            db_campaigns = query.order_by(CampaignDB.created_at.desc()).all()

            campaigns = []
            for db_campaign in db_campaigns:
                campaign = dict_to_campaign(db_campaign.data)
                campaigns.append(campaign)

            return campaigns

    def get_templates(self) -> list[Campaign]:
        """Get pre-built campaign templates."""
        with next(get_session()) as db:
            db_campaigns = db.query(CampaignDB).filter(CampaignDB.is_template).all()

            campaigns = []
            for db_campaign in db_campaigns:
                campaign = dict_to_campaign(db_campaign.data)
                campaigns.append(campaign)

            return campaigns

    def clone_campaign(
        self, template_id: str, new_name: str | None = None
    ) -> Campaign | None:
        """Clone a template campaign for customization."""
        template = self.get_campaign(template_id)
        if not template:
            return None

        # Create new campaign based on template
        cloned_campaign = Campaign(
            id=str(uuid.uuid4()),
            name=new_name or f"{template.name} (Copy)",
            description=template.description,
            setting=template.setting,
            tone=template.tone,
            homebrew_rules=template.homebrew_rules.copy()
            if template.homebrew_rules
            else [],
            world_description=template.world_description,
            world_art=template.world_art,
            is_custom=True,
            is_template=False,
            template_id=template_id,
        )

        # Save to database
        with next(get_session()) as db:
            db_campaign = CampaignDB(
                id=cloned_campaign.id,
                name=cloned_campaign.name,
                description=cloned_campaign.description,
                setting=cloned_campaign.setting,
                tone=cloned_campaign.tone,
                homebrew_rules=cloned_campaign.homebrew_rules,
                world_description=cloned_campaign.world_description,
                world_art=cloned_campaign.world_art,
                is_custom=True,
                is_template=False,
                template_id=template_id,
                data=campaign_to_dict(cloned_campaign),
            )
            db.add(db_campaign)
            db.commit()
            db.refresh(db_campaign)

        return cloned_campaign

    def update_campaign(
        self, campaign_id: str, updates: dict[str, Any]
    ) -> Campaign | None:
        """Update an existing campaign."""
        with next(get_session()) as db:
            db_campaign = (
                db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
            )
            if not db_campaign:
                return None

            # Update campaign data
            campaign_data = dict_to_campaign(db_campaign.data)

            # Create a clean update dict from the campaign_data model
            campaign_dict = campaign_data.model_dump()

            # Apply updates to the campaign dict, only for valid fields
            valid_fields = set(campaign_dict.keys())
            for key, value in updates.items():
                if key in valid_fields:
                    campaign_dict[key] = value

            # Create updated campaign object from the merged dict
            updated_campaign = Campaign.model_validate(campaign_dict)

            # Update database record with explicit field mappings
            if "name" in updates:
                db_campaign.name = updates["name"]
            if "description" in updates:
                db_campaign.description = updates["description"]
            if "setting" in updates:
                db_campaign.setting = updates["setting"]
            if "tone" in updates:
                db_campaign.tone = updates["tone"]
            if "homebrew_rules" in updates:
                db_campaign.homebrew_rules = updates["homebrew_rules"]
            if "world_description" in updates:
                db_campaign.world_description = updates["world_description"]
            if "world_art" in updates:
                db_campaign.world_art = updates["world_art"]

            db_campaign.data = campaign_to_dict(updated_campaign)
            db_campaign.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(db_campaign)

            return dict_to_campaign(db_campaign.data)

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign (only custom campaigns, not templates)."""
        with next(get_session()) as db:
            db_campaign = (
                db.query(CampaignDB)
                .filter(
                    CampaignDB.id == campaign_id,
                    not CampaignDB.is_template,  # Only allow deletion of non-templates
                )
                .first()
            )

            if db_campaign:
                db.delete(db_campaign)
                db.commit()
                return True
            return False

    def create_template_campaigns(self) -> None:
        """Create default template campaigns if they don't exist."""
        templates = [
            {
                "name": "Lost Mine of Phandelver",
                "description": "A classic starter adventure perfect for new players and DMs.",
                "setting": "The Sword Coast region of the Forgotten Realms, centered around the frontier town of Phandalin and the surrounding wilderness.",
                "tone": "heroic",
                "homebrew_rules": [],
                "world_description": "The sleepy frontier town of Phandalin lies on the Triboar Trail, a trade route connecting the coastal city of Neverwinter to the inland settlements. Recently, goblins have been raiding merchant caravans, threatening the town's prosperity. Meanwhile, rumors speak of a lost mine filled with magical treasures, somewhere in the nearby hills.",
                "plot_hooks": [
                    "Escort a supply wagon to Phandalin for Gundren Rockseeker",
                    "Investigate the goblin attacks on local merchants",
                    "Discover the location of the legendary Lost Mine of Phandelver",
                ],
                "key_npcs": [
                    "Gundren Rockseeker - Dwarf merchant with a secret",
                    "Sister Garaele - Half-elf cleric seeking ancient knowledge",
                    "Toblen Stonehill - Halfling innkeeper with local gossip",
                ],
            },
            {
                "name": "Dragon Heist",
                "description": "Urban intrigue and faction politics in the City of Splendors.",
                "setting": "Waterdeep, the bustling metropolis known as the City of Splendors, where noble houses scheme and hidden treasures await discovery.",
                "tone": "mysterious",
                "homebrew_rules": [],
                "world_description": "Waterdeep is a city of grand towers and crowded streets, where merchant princes rub shoulders with spies and adventurers. The city is divided into wards, each with its own character - from the wealthy Sea Ward to the dangerous Dock Ward. Recently, a cache of dragons' gold has gone missing, and every faction in the city wants to claim it.",
                "plot_hooks": [
                    "Investigate a mysterious explosion at a local tavern",
                    "Navigate the complex politics of Waterdeep's noble houses",
                    "Track down half a million gold dragons hidden somewhere in the city",
                ],
                "key_npcs": [
                    "Laeral Silverhand - Open Lord of Waterdeep",
                    "Vajra Safahr - Blackstaff of Waterdeep",
                    "Volothamp Geddarm - Famous chronicler and quest-giver",
                ],
            },
            {
                "name": "Curse of Strahd",
                "description": "Gothic horror in the mist-shrouded realm of Barovia.",
                "setting": "The demiplane of Barovia, a land trapped in mists and ruled by the vampire lord Strahd von Zarovich.",
                "tone": "dark",
                "homebrew_rules": [
                    "Characters cannot leave Barovia until Strahd is defeated",
                    "Death saves are made in secret by the DM",
                    "Resurrection magic has a chance to fail",
                ],
                "world_description": "Barovia is a land under a curse, shrouded in mist and ruled by the vampire Count Strahd von Zarovich. The sun rarely shines through the perpetual overcast sky, and the very land seems to work against those who would oppose its dark master. Villages huddle behind weak walls, their inhabitants living in fear of the creatures that emerge when darkness falls.",
                "plot_hooks": [
                    "Escape the mysterious mists that have transported you to this cursed land",
                    "Help the tormented souls trapped in Barovia find peace",
                    "Confront the ancient evil that rules this domain of dread",
                ],
                "key_npcs": [
                    "Strahd von Zarovich - The vampire lord of Barovia",
                    "Ireena Kolyana - The reincarnation of Strahd's lost love",
                    "Rudolph van Richten - Legendary monster hunter",
                ],
            },
            {
                "name": "Pirates of the Caribbean Coast",
                "description": "Swashbuckling adventures on the high seas.",
                "setting": "The Shining Sea and its many islands, where pirates, merchants, and naval forces clash over treasure and territory.",
                "tone": "lighthearted",
                "homebrew_rules": [
                    "Ship combat rules are simplified for narrative focus",
                    "Swimming and sailing checks are more common",
                    "Firearms are allowed and more prevalent",
                ],
                "world_description": "The warm waters of the Shining Sea are dotted with tropical islands, each harboring its own secrets. Port cities bustle with merchants, sailors, and rogues of every description. The line between privateer and pirate is often blurred, and fortunes can be made or lost with a single voyage. Ancient ruins hide treasures from lost civilizations, while sea monsters lurk in the depths.",
                "plot_hooks": [
                    "Search for a legendary pirate's buried treasure",
                    "Defend merchant ships from pirate attacks",
                    "Explore mysterious islands rumored to hold ancient secrets",
                ],
                "key_npcs": [
                    "Captain 'Bloody Mary' Blackwater - Notorious pirate captain",
                    "Admiral Thorne - Naval commander hunting pirates",
                    "Old Pete - Grizzled sailor with tales of buried treasure",
                ],
            },
            {
                "name": "Cyberpunk Shadows",
                "description": "High-tech corporate espionage in a dystopian future.",
                "setting": "Neo-Tokyo 2087, a sprawling megacity dominated by powerful corporations where technology and magic coexist.",
                "tone": "gritty",
                "homebrew_rules": [
                    "Technology items are more common and advanced",
                    "Cybernetic enhancements available for characters",
                    "Magic is rare and often suppressed by corporate interests",
                ],
                "world_description": "The year is 2087, and the world has changed. Massive corporations control every aspect of life in the sprawling megacities. Technology has advanced to incredible heights, but magic has also returned to the world, creating an uneasy balance. In the shadows between the gleaming corporate towers and the dark undercity, shadowrunners operate - freelance operatives who take on jobs that the corps can't or won't handle officially.",
                "plot_hooks": [
                    "Infiltrate a corporate facility to steal valuable data",
                    "Investigate mysterious magical phenomena in the city",
                    "Navigate the dangerous politics of corporate warfare",
                ],
                "key_npcs": [
                    "Akira Tanaka - Corporate executive with a hidden agenda",
                    "Zero - Mysterious hacker with ties to the underground",
                    "Dr. Elena Voss - Scientist studying the return of magic",
                ],
            },
        ]

        with next(get_session()) as db:
            for template_data in templates:
                # Check if template already exists
                existing = (
                    db.query(CampaignDB)
                    .filter(
                        CampaignDB.name == template_data["name"],
                        CampaignDB.is_template,
                    )
                    .first()
                )

                if not existing:
                    campaign_id = str(uuid.uuid4())
                    campaign = Campaign(
                        id=campaign_id,
                        name=template_data["name"],
                        description=template_data["description"],
                        setting=template_data["setting"],
                        tone=template_data["tone"],
                        homebrew_rules=template_data["homebrew_rules"],
                        world_description=template_data["world_description"],
                        is_template=True,
                        is_custom=False,
                        plot_hooks=template_data.get("plot_hooks", []),
                        key_npcs=template_data.get("key_npcs", []),
                    )

                    db_campaign = CampaignDB(
                        id=campaign_id,
                        name=template_data["name"],
                        description=template_data["description"],
                        setting=template_data["setting"],
                        tone=template_data["tone"],
                        homebrew_rules=template_data["homebrew_rules"],
                        world_description=template_data["world_description"],
                        is_template=True,
                        is_custom=False,
                        data=campaign_to_dict(campaign),
                    )
                    db.add(db_campaign)

            db.commit()


# Global service instance
campaign_service = CampaignService()

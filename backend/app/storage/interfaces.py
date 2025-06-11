"""
Storage abstraction interfaces for game data persistence.

This module defines abstract base classes for different types of game data storage
to support the hybrid approach with Semantic Memory as specified in ADR 0003.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


@dataclass
class StorageRecord:
    """A record stored in the game data storage system."""
    id: str
    content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class GameDataStorage(ABC):
    """
    Abstract base class for game data storage.
    
    This provides the abstraction layer recommended by ADR 0003 to allow
    alternative implementations and mitigate risks of dependency on Semantic Memory.
    """

    @abstractmethod
    async def store_character(self, character_data: Dict[str, Any]) -> str:
        """
        Store character data and return the character ID.
        
        Args:
            character_data: Dictionary containing character information
            
        Returns:
            str: The ID of the stored character
        """
        pass

    @abstractmethod
    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve character data by ID.
        
        Args:
            character_id: The ID of the character to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Character data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update character data.
        
        Args:
            character_id: The ID of the character to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_character(self, character_id: str) -> bool:
        """
        Delete character data.
        
        Args:
            character_id: The ID of the character to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    async def search_characters(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for characters using natural language queries.
        
        Args:
            query: Natural language search query
            filters: Optional filters to apply
            
        Returns:
            List[Dict[str, Any]]: List of matching characters
        """
        pass

    @abstractmethod
    async def store_npc(self, npc_data: Dict[str, Any]) -> str:
        """Store NPC data and return the NPC ID."""
        pass

    @abstractmethod
    async def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve NPC data by ID."""
        pass

    @abstractmethod
    async def update_npc(self, npc_id: str, updates: Dict[str, Any]) -> bool:
        """Update NPC data."""
        pass

    @abstractmethod
    async def delete_npc(self, npc_id: str) -> bool:
        """Delete NPC data."""
        pass

    @abstractmethod
    async def search_npcs(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for NPCs using natural language queries."""
        pass

    @abstractmethod
    async def store_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Store campaign data and return the campaign ID."""
        pass

    @abstractmethod
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve campaign data by ID."""
        pass

    @abstractmethod
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign data."""
        pass

    @abstractmethod
    async def store_game_event(self, event_data: Dict[str, Any]) -> str:
        """Store a game event/narrative entry."""
        pass

    @abstractmethod
    async def search_events(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for game events using natural language queries."""
        pass


class AssetStorage(ABC):
    """
    Abstract base class for game asset storage (images, maps, etc.).
    
    Handles binary asset storage separate from structured game data.
    """

    @abstractmethod
    async def store_asset(self, asset_data: bytes, asset_type: str, metadata: Dict[str, Any]) -> str:
        """
        Store a binary asset and return its ID.
        
        Args:
            asset_data: Binary data of the asset
            asset_type: Type of asset (image, map, etc.)
            metadata: Asset metadata
            
        Returns:
            str: Asset ID
        """
        pass

    @abstractmethod
    async def get_asset(self, asset_id: str) -> Optional[bytes]:
        """Retrieve asset data by ID."""
        pass

    @abstractmethod
    async def get_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve asset metadata by ID."""
        pass

    @abstractmethod
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset by ID."""
        pass
"""
Semantic Memory-based implementation of game data storage.

This implementation uses Semantic Kernel's memory systems as the primary storage
mechanism, as specified in ADR 0003's chosen "Hybrid Approach with Semantic Memory".
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from semantic_kernel.memory import SemanticTextMemory, MemoryRecord
from semantic_kernel.memory.volatile_memory_store import VolatileMemoryStore
from semantic_kernel.connectors.ai.embeddings.embedding_generator_base import EmbeddingGeneratorBase

from app.storage.interfaces import GameDataStorage, StorageRecord

logger = logging.getLogger(__name__)


class SemanticGameDataStorage(GameDataStorage):
    """
    Semantic Memory-based implementation of game data storage.
    
    Uses Semantic Kernel's memory systems for storage and retrieval with
    natural language query capabilities.
    """

    def __init__(self, embedding_generator: Optional[EmbeddingGeneratorBase] = None):
        """
        Initialize the semantic storage system.
        
        Args:
            embedding_generator: Optional embedding generator for semantic search.
                                If None, will use a simple in-memory store without embeddings.
        """
        self.embedding_generator = embedding_generator
        
        # Create memory store - start with volatile for now, can be replaced with persistent store
        self.memory_store = VolatileMemoryStore()
        
        # Create semantic memory if embedding generator is available
        if embedding_generator:
            self.semantic_memory = SemanticTextMemory(
                storage=self.memory_store,
                embeddings_generator=embedding_generator
            )
        else:
            self.semantic_memory = None
            logger.warning("No embedding generator provided. Semantic search will not be available.")

        # Collection names for different data types
        self.CHARACTERS_COLLECTION = "characters"
        self.NPCS_COLLECTION = "npcs"
        self.CAMPAIGNS_COLLECTION = "campaigns"
        self.EVENTS_COLLECTION = "events"

    async def _ensure_collection_exists(self, collection_name: str):
        """Ensure a memory collection exists."""
        try:
            collections = await self.memory_store.get_collections()
            if collection_name not in collections:
                await self.memory_store.create_collection(collection_name)
        except Exception as e:
            logger.error(f"Error ensuring collection {collection_name} exists: {str(e)}")
            raise

    async def _store_record(self, collection: str, record_id: str, data: Dict[str, Any], 
                           search_text: str = None) -> str:
        """
        Store a record in the specified collection.
        
        Args:
            collection: Collection name
            record_id: Record ID
            data: Data to store
            search_text: Text to use for semantic search (optional)
            
        Returns:
            str: The stored record ID
        """
        try:
            await self._ensure_collection_exists(collection)
            
            # Prepare metadata
            metadata = {
                "type": collection,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # If we have semantic memory, use it for searchable content
            if self.semantic_memory and search_text:
                await self.semantic_memory.save_information(
                    collection=collection,
                    text=search_text,
                    id=record_id,
                    additional_metadata=json.dumps({**data, **metadata})
                )
            else:
                # Fallback to direct memory store
                record = MemoryRecord(
                    id=record_id,
                    text=search_text or json.dumps(data),
                    additional_metadata=json.dumps({**data, **metadata}),
                    embedding=[]  # Empty embedding for non-semantic storage
                )
                await self.memory_store.upsert(collection, record)
            
            return record_id
        except Exception as e:
            logger.error(f"Error storing record in {collection}: {str(e)}")
            raise

    async def _get_record(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a record from the specified collection."""
        try:
            await self._ensure_collection_exists(collection)
            
            record = await self.memory_store.get(collection, record_id)
            if record:
                # Parse the metadata which contains our data
                return json.loads(record.additional_metadata)
            return None
        except Exception as e:
            logger.error(f"Error retrieving record {record_id} from {collection}: {str(e)}")
            return None

    async def _update_record(self, collection: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update a record in the specified collection."""
        try:
            # Get existing record
            existing_data = await self._get_record(collection, record_id)
            if not existing_data:
                return False
            
            # Merge updates
            existing_data.update(updates)
            existing_data["updated_at"] = datetime.now().isoformat()
            
            # Store updated record
            search_text = self._generate_search_text(existing_data, collection)
            await self._store_record(collection, record_id, existing_data, search_text)
            return True
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {collection}: {str(e)}")
            return False

    async def _delete_record(self, collection: str, record_id: str) -> bool:
        """Delete a record from the specified collection."""
        try:
            await self._ensure_collection_exists(collection)
            await self.memory_store.remove(collection, record_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {collection}: {str(e)}")
            return False

    async def _search_records(self, collection: str, query: str, 
                             filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search records in a collection using semantic or text-based search."""
        try:
            await self._ensure_collection_exists(collection)
            
            if self.semantic_memory:
                # Use semantic search
                results = await self.semantic_memory.search(
                    collection=collection,
                    query=query,
                    limit=10  # Default limit
                )
                
                records = []
                for result in results:
                    record_data = json.loads(result.metadata.additional_metadata)
                    
                    # Apply filters if provided
                    if filters and not self._matches_filters(record_data, filters):
                        continue
                        
                    records.append(record_data)
                
                return records
            else:
                # Fallback to simple text search in stored data
                # This is a simplified implementation - in production you'd want better search
                logger.warning("Performing simple text search - semantic search not available")
                return []
                
        except Exception as e:
            logger.error(f"Error searching in {collection}: {str(e)}")
            return []

    def _matches_filters(self, record: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if a record matches the provided filters."""
        for key, value in filters.items():
            if key not in record or record[key] != value:
                return False
        return True

    def _generate_search_text(self, data: Dict[str, Any], collection: str) -> str:
        """Generate searchable text from data based on collection type."""
        if collection == self.CHARACTERS_COLLECTION:
            return f"Character: {data.get('name', '')} " \
                   f"Race: {data.get('race', '')} " \
                   f"Class: {data.get('class', '')} " \
                   f"Level: {data.get('level', '')} " \
                   f"Background: {data.get('backstory', '')}"
        elif collection == self.NPCS_COLLECTION:
            return f"NPC: {data.get('name', '')} " \
                   f"Description: {data.get('description', '')} " \
                   f"Location: {data.get('location', '')} " \
                   f"Relationships: {data.get('relationships', '')}"
        elif collection == self.CAMPAIGNS_COLLECTION:
            return f"Campaign: {data.get('name', '')} " \
                   f"Setting: {data.get('setting', '')} " \
                   f"Description: {data.get('description', '')}"
        elif collection == self.EVENTS_COLLECTION:
            return f"Event: {data.get('description', '')} " \
                   f"Location: {data.get('location', '')} " \
                   f"Characters: {', '.join(data.get('characters', []))}"
        else:
            return json.dumps(data)

    # Character storage methods
    async def store_character(self, character_data: Dict[str, Any]) -> str:
        """Store character data and return the character ID."""
        character_id = character_data.get("id", str(uuid.uuid4()))
        character_data["id"] = character_id
        
        search_text = self._generate_search_text(character_data, self.CHARACTERS_COLLECTION)
        await self._store_record(self.CHARACTERS_COLLECTION, character_id, character_data, search_text)
        return character_id

    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve character data by ID."""
        return await self._get_record(self.CHARACTERS_COLLECTION, character_id)

    async def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """Update character data."""
        return await self._update_record(self.CHARACTERS_COLLECTION, character_id, updates)

    async def delete_character(self, character_id: str) -> bool:
        """Delete character data."""
        return await self._delete_record(self.CHARACTERS_COLLECTION, character_id)

    async def search_characters(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for characters using natural language queries."""
        return await self._search_records(self.CHARACTERS_COLLECTION, query, filters)

    # NPC storage methods
    async def store_npc(self, npc_data: Dict[str, Any]) -> str:
        """Store NPC data and return the NPC ID."""
        npc_id = npc_data.get("id", str(uuid.uuid4()))
        npc_data["id"] = npc_id
        
        search_text = self._generate_search_text(npc_data, self.NPCS_COLLECTION)
        await self._store_record(self.NPCS_COLLECTION, npc_id, npc_data, search_text)
        return npc_id

    async def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve NPC data by ID."""
        return await self._get_record(self.NPCS_COLLECTION, npc_id)

    async def update_npc(self, npc_id: str, updates: Dict[str, Any]) -> bool:
        """Update NPC data."""
        return await self._update_record(self.NPCS_COLLECTION, npc_id, updates)

    async def delete_npc(self, npc_id: str) -> bool:
        """Delete NPC data."""
        return await self._delete_record(self.NPCS_COLLECTION, npc_id)

    async def search_npcs(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for NPCs using natural language queries."""
        return await self._search_records(self.NPCS_COLLECTION, query, filters)

    # Campaign storage methods
    async def store_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Store campaign data and return the campaign ID."""
        campaign_id = campaign_data.get("id", str(uuid.uuid4()))
        campaign_data["id"] = campaign_id
        
        search_text = self._generate_search_text(campaign_data, self.CAMPAIGNS_COLLECTION)
        await self._store_record(self.CAMPAIGNS_COLLECTION, campaign_id, campaign_data, search_text)
        return campaign_id

    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve campaign data by ID."""
        return await self._get_record(self.CAMPAIGNS_COLLECTION, campaign_id)

    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign data."""
        return await self._update_record(self.CAMPAIGNS_COLLECTION, campaign_id, updates)

    # Event storage methods
    async def store_game_event(self, event_data: Dict[str, Any]) -> str:
        """Store a game event/narrative entry."""
        event_id = event_data.get("id", str(uuid.uuid4()))
        event_data["id"] = event_id
        
        search_text = self._generate_search_text(event_data, self.EVENTS_COLLECTION)
        await self._store_record(self.EVENTS_COLLECTION, event_id, event_data, search_text)
        return event_id

    async def search_events(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for game events using natural language queries."""
        return await self._search_records(self.EVENTS_COLLECTION, query, filters)
"""
OpenAPI Schema Validation Tests.
Tests to ensure backend API schema is accessible and valid for frontend client generation.
"""

import pytest
import sys
import os
import json
import subprocess
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestOpenAPISchemaValidation:
    """Test OpenAPI schema accessibility and validation."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_openapi_schema_endpoint_accessible(self, client):
        """Test that the OpenAPI schema endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200, "OpenAPI schema endpoint should be accessible"
        
        # Verify it returns valid JSON
        schema = response.json()
        assert isinstance(schema, dict), "OpenAPI schema should be a JSON object"
        
        # Verify it has required OpenAPI fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert field in schema, f"OpenAPI schema missing required field: {field}"

    def test_openapi_schema_structure(self, client):
        """Test that the OpenAPI schema has the expected structure."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Check OpenAPI version
        assert "openapi" in schema
        assert schema["openapi"].startswith("3."), "Should use OpenAPI 3.x specification"
        
        # Check info section
        assert "info" in schema
        info = schema["info"]
        assert "title" in info
        assert "version" in info
        assert info["title"] == "AI Dungeon Master API"
        
        # Check paths section
        assert "paths" in schema
        paths = schema["paths"]
        assert isinstance(paths, dict), "Paths should be a dictionary"
        
        # Verify key API endpoints are documented
        expected_endpoints = [
            "/api/game/character",
            "/api/game/campaign", 
            "/api/game/input",
            "/health"
        ]
        
        for endpoint in expected_endpoints:
            assert any(endpoint in path for path in paths.keys()), f"Missing endpoint in schema: {endpoint}"

    def test_openapi_schema_components(self, client):
        """Test that the OpenAPI schema includes component definitions."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Check components section exists
        assert "components" in schema, "OpenAPI schema should include components section"
        components = schema["components"]
        
        # Check schemas are defined
        assert "schemas" in components, "Components should include schemas"
        schemas = components["schemas"]
        
        # Verify key model schemas are present
        expected_schemas = [
            "CreateCharacterRequest",
            "CharacterSheet", 
            "CreateCampaignRequest",
            "Campaign",
            "PlayerInput",
            "GameResponse"
        ]
        
        for schema_name in expected_schemas:
            assert schema_name in schemas, f"Missing schema definition: {schema_name}"

    def test_character_endpoint_schema_compatibility(self, client):
        """Test that character endpoint schema matches frontend expectations."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Find the character creation endpoint
        character_endpoint = None
        for path, methods in schema["paths"].items():
            if "/character" in path and "post" in methods:
                character_endpoint = methods["post"]
                break
        
        assert character_endpoint is not None, "Character creation endpoint not found in schema"
        
        # Check request body schema
        assert "requestBody" in character_endpoint
        request_body = character_endpoint["requestBody"]
        assert "content" in request_body
        assert "application/json" in request_body["content"]
        
        # Check response schema
        assert "responses" in character_endpoint
        responses = character_endpoint["responses"]
        assert "200" in responses or "201" in responses, "Should have success response"

    def test_campaign_endpoint_schema_compatibility(self, client):
        """Test that campaign endpoint schema matches frontend expectations."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Find the campaign creation endpoint
        campaign_endpoint = None
        for path, methods in schema["paths"].items():
            if "/campaign" in path and "post" in methods:
                campaign_endpoint = methods["post"]
                break
        
        assert campaign_endpoint is not None, "Campaign creation endpoint not found in schema"
        
        # Check request body schema
        assert "requestBody" in campaign_endpoint
        request_body = campaign_endpoint["requestBody"]
        assert "content" in request_body
        assert "application/json" in request_body["content"]

    def test_schema_enum_values_match_frontend(self, client):
        """Test that enum values in schema match frontend expectations."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        schemas = schema.get("components", {}).get("schemas", {})
        
        # Check Race enum if present
        if "Race" in schemas:
            race_schema = schemas["Race"]
            if "enum" in race_schema:
                race_values = race_schema["enum"]
                # Should use lowercase values as expected by frontend
                assert "human" in race_values or "Human" in race_values
                assert "elf" in race_values or "Elf" in race_values
        
        # Check CharacterClass enum if present
        if "CharacterClass" in schemas:
            class_schema = schemas["CharacterClass"]
            if "enum" in class_schema:
                class_values = class_schema["enum"]
                # Should use lowercase values as expected by frontend
                assert "fighter" in class_values or "Fighter" in class_values
                assert "wizard" in class_values or "Wizard" in class_values

    def test_required_fields_documented(self, client):
        """Test that required fields are properly documented in schema."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        schemas = schema.get("components", {}).get("schemas", {})
        
        # Check CreateCharacterRequest has required fields
        if "CreateCharacterRequest" in schemas:
            char_schema = schemas["CreateCharacterRequest"]
            if "required" in char_schema:
                required_fields = char_schema["required"]
                expected_required = ["name", "race", "character_class", "abilities"]
                for field in expected_required:
                    assert field in required_fields, f"Missing required field in schema: {field}"

    def test_docs_endpoint_accessible(self, client):
        """Test that the interactive docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200, "Interactive docs should be accessible"

    def test_redoc_endpoint_accessible(self, client):
        """Test that the ReDoc endpoint is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200, "ReDoc documentation should be accessible"

    def test_schema_validation_for_client_generation(self, client):
        """Test that the schema is valid for TypeScript client generation."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Basic validation that the schema can be used for code generation
        assert "paths" in schema
        assert len(schema["paths"]) > 0, "Schema should have API paths defined"
        
        assert "components" in schema
        assert "schemas" in schema["components"]
        assert len(schema["components"]["schemas"]) > 0, "Schema should have model definitions"
        
        # Check for common issues that break client generation
        for path, methods in schema["paths"].items():
            for method, operation in methods.items():
                if "responses" in operation:
                    # Each operation should have at least one response defined
                    assert len(operation["responses"]) > 0, f"Operation {method} {path} missing responses"

    def test_frontend_client_generation_compatibility(self):
        """Test that the OpenAPI schema can be used to generate a TypeScript client."""
        # This test verifies the schema is compatible with openapi-generator-cli
        # It doesn't actually run the generation (which requires the server to be running)
        # but validates the schema structure needed for generation
        
        # Check if we can import and validate the main app without errors
        from app.main import app
        assert app is not None, "FastAPI app should be importable"
        
        # Verify the app has the expected configuration for OpenAPI
        assert app.title == "AI Dungeon Master API"
        assert app.version == "0.1.0"
        
        # Check that routers are properly included
        assert len(app.routes) > 0, "App should have routes configured"

    def test_model_serialization_compatibility(self):
        """Test that Pydantic models serialize correctly for OpenAPI schema."""
        from app.models.game_models import (
            CreateCharacterRequest,
            CharacterSheet,
            CreateCampaignRequest,
            Campaign,
            Race,
            CharacterClass,
            Abilities
        )
        
        # Test that models can be serialized to JSON schema
        abilities = Abilities(strength=16, dexterity=14, constitution=15)
        char_request = CreateCharacterRequest(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities
        )
        
        # Should be able to serialize to dict (used by FastAPI for OpenAPI schema)
        char_dict = char_request.model_dump()
        assert isinstance(char_dict, dict)
        assert "name" in char_dict
        assert "race" in char_dict
        assert "character_class" in char_dict
        assert "abilities" in char_dict
        
        # Test enum serialization
        assert char_dict["race"] in ["human", "Human"]  # Should be serializable
        assert char_dict["character_class"] in ["fighter", "Fighter"]  # Should be serializable
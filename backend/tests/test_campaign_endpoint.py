"""
Test to reproduce the campaign endpoint issue.
"""
import os
from fastapi.testclient import TestClient

def test_campaign_endpoint_with_missing_config():
    """Test that campaign endpoint properly handles missing Azure OpenAI configuration."""
    
    # Temporarily clear Azure OpenAI environment variables
    env_vars_to_clear = [
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_CHAT_DEPLOYMENT",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]
    
    original_values = {}
    for var in env_vars_to_clear:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        # Import after clearing environment to ensure settings get the missing values
        from app.main import app
        
        client = TestClient(app)
        
        # Test campaign creation with missing config
        campaign_data = {
            "name": "Test Campaign",
            "setting": "fantasy", 
            "tone": "heroic"
        }
        
        response = client.post("/api/game/campaign", json=campaign_data)
        
        # We expect a service unavailable error (503) with proper error message about Azure OpenAI
        if response.status_code == 404:
            print("ERROR: Got 404 - this is the bug we need to fix")
        elif response.status_code == 503:
            response_data = response.json()
            if "Azure OpenAI" in response_data.get("detail", ""):
                print("GOOD: Got 503 Service Unavailable with proper error about missing Azure OpenAI configuration")
            else:
                print(f"Got 503 but unclear error: {response_data}")
        elif response.status_code == 500:
            response_data = response.json()
            if "Azure OpenAI" in response_data.get("detail", ""):
                print("GOOD: Got proper error about missing Azure OpenAI configuration")
            else:
                print(f"Got 500 but unclear error: {response_data}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            
        return response
        
    finally:
        # Restore original environment values
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

if __name__ == "__main__":
    test_campaign_endpoint_with_missing_config()